import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import struct
import numpy as np
from PIL import Image, ImageTk
import math
import os

matrix = None

def read_bmp(file_path):
    with open(file_path, 'rb') as f:
        file_header = f.read(14)
        if len(file_header) < 14:
            raise ValueError("File too small to be a BMP")
        if file_header[0:2] != b'BM':
            raise ValueError("Not a BMP file (invalid signature)")

        data_offset = struct.unpack('<I', file_header[10:14])[0]
        info_header = f.read(40)
        if len(info_header) < 40:
            raise ValueError("Incomplete BMP info header")

        width       = struct.unpack('<i', info_header[4:8])[0]
        height      = struct.unpack('<i', info_header[8:12])[0]
        bit_count   = struct.unpack('<H', info_header[14:16])[0]
        compression = struct.unpack('<I', info_header[16:20])[0]

        bottom_up  = height > 0
        abs_height = abs(height)

        palette = []
        if bit_count == 8:
            f.seek(14 + 40)
            for i in range(256):
                b, g, r, _ = f.read(4)
                palette.append([r, g, b])
        elif bit_count == 4:
            f.seek(14 + 40)
            for i in range(16):
                b, g, r, _ = f.read(4)
                palette.append([r, g, b])

        if bit_count == 24:
            row_size = ((width * 3 + 3) // 4) * 4
        elif bit_count == 32:
            row_size = width * 4
        elif bit_count == 8:
            row_size = ((width + 3) // 4) * 4
        elif bit_count == 4:
            row_size = ((width + 1) // 2 + 3) // 4 * 4
        elif bit_count == 16:
            row_size = ((width * 2 + 3) // 4) * 4
        else:
            raise ValueError(f"Unsupported bit count: {bit_count}")

        f.seek(data_offset)
        pixels = []
        for _ in range(abs_height):
            row_data = f.read(row_size)
            if len(row_data) < row_size:
                raise ValueError("Unexpected end of file")
            row_pixels = []
            if bit_count == 24:
                for x in range(width):
                    b = row_data[x * 3]
                    g = row_data[x * 3 + 1]
                    r = row_data[x * 3 + 2]
                    row_pixels.append([r, g, b])

            elif bit_count == 32:
                for x in range(width):
                    b = row_data[x * 4]
                    g = row_data[x * 4 + 1]
                    r = row_data[x * 4 + 2]
                    row_pixels.append([r, g, b])

            elif bit_count == 8:
                for x in range(width):
                    index = row_data[x]
                    row_pixels.append(palette[index])

            elif bit_count == 4:
                for x in range(width):
                    byte = row_data[x // 2]
                    if x % 2 == 0:
                        index = (byte >> 4) & 0x0F 
                    else:
                        index = byte & 0x0F
                    row_pixels.append(palette[index])

            elif bit_count == 16:
                for x in range(width):
                    pixel = struct.unpack('<H', row_data[x*2:x*2+2])[0]
                    if compression == 3: 
                        r = ((pixel >> 11) & 0x1F) * 255 // 31
                        g = ((pixel >> 5)  & 0x3F) * 255 // 63
                        b = ( pixel        & 0x1F) * 255 // 31
                    else: 
                        r = ((pixel >> 10) & 0x1F) * 255 // 31
                        g = ((pixel >> 5)  & 0x1F) * 255 // 31
                        b = ( pixel        & 0x1F) * 255 // 31
                    row_pixels.append([r, g, b])
                    
            pixels.append(row_pixels)

        if bottom_up:
            pixels.reverse()

        return pixels


def open_image():
    file_path = filedialog.askopenfilename(
        title="Select a BMP Image",
        filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")]
    )

    if not file_path:
        print("No file selected.")
        return

    try:
        global matrix
        matrix = read_bmp(file_path)
        afiseaza(matrix, canvas_original)
        canvas_2.delete('all')
    except Exception as e:
        print(f"Error: {e}")

def mod_gray(matrix, method):
    res = [] 
    for row in matrix:
        new_row = []
        for pixel in row:
            r, g, b = pixel[0], pixel[1], pixel[2]
            if method == 1:
                gray = (r + g + b) / 3
            elif method == 2:
                gray = 0.299*r + 0.587*g + 0.114*b
            elif method == 3:
                gray = min(r,g,b)/2 + max(r,g,b)/2
            new_row.append([int(gray), int(gray), int(gray)])
        res.append(new_row)
    return res

def convert_cmyk(matrix):
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            r, g, b = pixel[0], pixel[1], pixel[2]
            c = 1 - (r/255)
            m = 1 - (g/255)
            y = 1 - (b/255)
            k = min(c,m,y)
            if k == 1: 
                ck, mk, yk = 0, 0, 0
            else:
                ck = (c - k) / (1 - k)
                mk = (m - k) / (1 - k)
                yk = (y - k) / (1 - k)
            new_row.append([int(ck*255), int(mk*255), int(yk*255), int(k*255)])
        res.append(new_row)
    return res

def convert_yuv(matrix):
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            r, g, b = pixel[0], pixel[1], pixel[2]
            y = 0.3*r + 0.6*g + 0.1*b 
            u = 0.74*(r-y) + 0.27*(b-y) # pot as fie valori negative
            v = 0.48*(r-y) + 0.41*(b-y) # pot sa fie valori negative
            new_row.append([
                int(max(0, min(255, y))),
                int(max(0, min(255, u + 128))),
                int(max(0, min(255, v + 128)))
            ]) # spre exemplu -10 devine 246
        res.append(new_row)
    return res

def convert_yCbCr(matrix):
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            r, g, b = pixel[0], pixel[1], pixel[2]
            y = 0.299 * r + 0.587*g + 0.114*b
            cb = -0.1687*r - 0.3313*g + 0.498*b + 128
            cr = 0.498*r - 0.4187*g - 0.0813*b + 128
            new_row.append([
                int(max(0, min(255, y))),
                int(max(0, min(255, cb))),
                int(max(0, min(255,cr)))
            ])
        res.append(new_row)
    return res
 
def inversare(matrix):
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            new_row.append([255 - pixel[0], 255 - pixel[1], 255 - pixel[2]])
        res.append(new_row)
    return res

def get_channel(matrix, channel):
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            p = pixel[channel]
            if channel == 0:
                new_row.append([p, 0, 0])  # doar rosu
            elif channel == 1:
                new_row.append([0, p, 0])  # doar verde
            elif channel == 2:
                new_row.append([0, 0, p])  # doar albastru
        res.append(new_row)
    return res

def show_invert():
    if matrix is None:
        return
    inv = inversare(matrix)
    afiseaza(inv, canvas_2)
    afiseaza(get_channel(inv, 0), canvas_r)
    afiseaza(get_channel(inv, 1), canvas_g) 
    afiseaza(get_channel(inv, 2), canvas_b)
    show_channels()

def show_channels():
    frame_channels.pack()

def hide_channels():
    canvas_r.delete('all')
    canvas_g.delete('all')
    canvas_b.delete('all')
    frame_channels.pack_forget()

def binarize(matrix, threshold=110):
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            gray = int(0.299*pixel[0] + 0.587*pixel[1] + 0.114*pixel[2]) # ochiul percepe intensitatea culorilor diferit, e cel mai sensibil la verde
            if gray >= threshold: # apoi rosu si apoi alabstru, toti coeficientii adunati trebuie sa dea 1
                val = 255
            else: val = 0 
            new_row.append([val, val, val])
        res.append(new_row)
    return res

def convert_hsv(matrix):
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            r, g, b = pixel[0]/255.0, pixel[1]/255.0, pixel[2]/255.0
            M = max(r,g,b)
            m = min(r,g,b)
            C = M-m

            V = M
            # saturatie
            S = C/V if V != 0 else 0

            # hue
            H = 0
            if C != 0:
                if M == r: H = 60*(g-b) / C
                if M == g: H = 120 + 60*(b-r) / C
                if M == b: H = 240 + 60*(r-g) / C
            if H < 0: H = H + 360

            # normalizare
            h_norm = H * 255/360
            s_norm = S * 255
            v_norm = V * 255
            new_row.append([h_norm, s_norm, v_norm])
        res.append(new_row)
    return res

def show_histogram(matrix):
    
    hist = [0] * 256
    for row in matrix:
        for pixel in row:
            gray = int((pixel[0] + pixel[1] + pixel[2]) / 3)
            hist[gray] += 1
            
    plt.figure("Histograma", figsize=(5,2))
    plt.bar(range(256), hist, color='gray', width=1, edgecolor='none')
    plt.xlim(0,255)
    plt.tight_layout()
    # plt.title("Histograma intensitatii de gri")
    # plt.xlabel("Nivel de gri")
    # plt.ylabel("Numar pixeli")
    plt.show()

def matrice_covarianta(mu20, mu02, mu11):
    cov = [
        [mu20, mu11],
        [mu11, mu02]
    ]
    print("\nMatricea de covarianta:")
    print(f"[ {mu20:.2f}   {mu11:.2f} ]")
    print(f"[ {mu11:.2f}   {mu02:.2f} ]")

    return cov

def calcul_momente(bin_matrix):
    """
    Calculeaza:
    - m00 (aria)
    - centrul de masa (xc, yc)
    - momente centrale de ordin 2 (mu20, mu02, mu11)
    """
    m00 = 0
    m10 = 0
    m01 = 0

    h = len(bin_matrix)
    w = len(bin_matrix[0])

    # Momente de ordin 0 si 1
    for y in range(h):
        for x in range(w):
            if bin_matrix[y][x][0] == 255:
                m00 += 1
                m10 += x
                m01 += y

    if m00 == 0:
        print("Nu exista obiect.")
        return None

    xc = m10 / m00
    yc = m01 / m00

    # Momente centrale de ordin 2
    mu20 = 0
    mu02 = 0
    mu11 = 0

    for y in range(h):
        for x in range(w):
            if bin_matrix[y][x][0] == 255:
                mu20 += (x - xc) ** 2
                mu02 += (y - yc) ** 2
                mu11 += (x - xc) * (y - yc)

    mu20 /= m00
    mu02 /= m00
    mu11 /= m00

    unghi_radiani = 0.5 * math.atan2(2 * mu11, mu20 - mu02)
    unghi_grade = math.degrees(unghi_radiani)

    print("\n--- ANALIZA FORMA ---")
    print(f"Aria (m00): {m00}")
    print(f"Centru masa: ({xc:.2f}, {yc:.2f})")
    print(f"Orientare: {unghi_radiani:.2f} radiani")
    print(f"Orientare: {unghi_grade:.2f} grade")
    print(f"mu20: {mu20:.2f}")
    print(f"mu02: {mu02:.2f}")
    print(f"mu11: {mu11:.2f}")
    matrice_covarianta(mu20, mu02, mu11)
    return xc, yc, mu20, mu02, mu11

def calcul_proiectii(bin_matrix):
    h = len(bin_matrix)
    w = len(bin_matrix[0])
    
    proiectie_H = [0] * h
    proiectie_V = [0] * w
    
    for y in range(h):
        for x in range(w):
            if bin_matrix[y][x][0] == 255:
                proiectie_H[y] += 1
                proiectie_V[x] += 1
    
    plt.figure("Proiectii")
    
    plt.subplot(2, 1, 1)
    plt.plot(proiectie_H, color='blue')
    plt.title("Proiectia pe Orizontala (Linii)")
    
    plt.subplot(2, 1, 2)
    plt.plot(proiectie_V, color='red')
    plt.title("Proiectia pe Verticala (Coloane)")
    
    plt.tight_layout()
    plt.show()

def afiseaza(mat, canvas):
    arr = np.array(mat, dtype=np.uint8)
    img = Image.fromarray(arr)
    imgtk = ImageTk.PhotoImage(img)
    canvas.config(width=img.width, height=img.height)
    canvas.create_image(0, 0, anchor="nw", image=imgtk)
    canvas.image = imgtk

root = tk.Tk()
root.title("BMP Image Loader")


frame_butoane = tk.Frame(root)
frame_butoane.pack()

tk.Button(frame_butoane, text="Open Image", command=open_image).pack(side="left", padx=5)
tk.Button(frame_butoane, text="Gray 1", command=lambda: [hide_channels(), afiseaza(mod_gray(matrix, 1), canvas_2)]).pack(side="left", padx=5)
tk.Button(frame_butoane, text="Gray 2", command=lambda: [hide_channels(), afiseaza(mod_gray(matrix, 2), canvas_2)]).pack(side="left", padx=5)
tk.Button(frame_butoane, text="Gray 3", command=lambda: [hide_channels(), afiseaza(mod_gray(matrix, 3), canvas_2)]).pack(side="left", padx=5)
tk.Button(frame_butoane, text="CMYK", command=lambda: [hide_channels(), afiseaza(convert_cmyk(matrix), canvas_2)]).pack(side="left", padx=5)
tk.Button(frame_butoane, text="YUV", command=lambda: [hide_channels(), afiseaza(convert_yuv(matrix), canvas_2)]).pack(side="left", padx=5)
tk.Button(frame_butoane, text="YCbCr", command=lambda: [hide_channels(), afiseaza(convert_yCbCr(matrix), canvas_2)]).pack(side="left", padx=5)
tk.Button(frame_butoane, text="Invert", command=show_invert).pack(side="left", padx=5)
tk.Button(frame_butoane, text="Binarizare", command=lambda: [hide_channels(), afiseaza(binarize(matrix), canvas_2)]).pack(side="left", padx=5)
tk.Button(frame_butoane, text="HSV", command=lambda: [hide_channels(), afiseaza(convert_hsv(matrix), canvas_2)]).pack(side="left", padx=5)
tk.Button(frame_butoane, text="Histograma", command=lambda: show_histogram(matrix)).pack(side="left", padx=5)
tk.Button(frame_butoane, text="Momente", command=lambda: calcul_momente(binarize(matrix))).pack(side="left", padx=5)
tk.Button(frame_butoane, text="Proiectii", command=lambda: calcul_proiectii(binarize(matrix))).pack(side="left", padx=5)

frame_poze = tk.Frame(root)
frame_poze.pack()

canvas_original = tk.Canvas(frame_poze)
canvas_original.pack(side="left")

canvas_2 = tk.Canvas(frame_poze)
canvas_2.pack(side="left")

# frame canale din imaginea inversata
frame_channels = tk.Frame(root)

canvas_r = tk.Canvas(frame_channels)
canvas_r.pack(side="left")

canvas_g = tk.Canvas(frame_channels)
canvas_g.pack(side="left")

canvas_b = tk.Canvas(frame_channels)
canvas_b.pack(side="left")

root.mainloop()