import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import struct
import numpy as np
from PIL import Image, ImageTk
import math

matrix = None
inv_matrix = None

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

        return pixels, width, abs_height, bit_count


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
        matrix, w, h, bits = read_bmp(file_path)
        filename = file_path.split("/")[-1]
        status_var.set(f"{filename}  |  {w} x {h} px  |  {bits} bpp")
        afiseaza(matrix, canvas_original)
        canvas_2.delete('all')
        clear_analysis()
    except Exception as e:
        print(f"Error: {e}")

def resetare():
    global inv_matrix, matrix
    canvas_2.delete('all')
    clear_analysis()
    status_var.set("Niciun fisier deschis.")
    inv_matrix = None
    matrix = None
    canvas_original.delete('all')

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
            rn = 1 - (r/255)
            gn = 1 - (g/255)
            bn = 1 - (b/255)
            k = min(rn,gn,bn)
            if k == 1: 
                c, m, y = 0, 0, 0
            else:
                c = (rn - k) / (1 - k)
                m = (gn - k) / (1 - k)
                y = (bn - k) / (1 - k)
            new_row.append([int(c*255), int(m*255), int(y*255)])
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

def show_invert(option):
    global inv_matrix
    if option == 1:
        if matrix is None:
            return
        inv_matrix = inversare(matrix)
        afiseaza(inv_matrix, canvas_2)
    else:
        if inv_matrix is None:
            return
        if option == 2:
            afiseaza(get_channel(inv_matrix, 0), canvas_2)
        elif option == 3:
            afiseaza(get_channel(inv_matrix, 1), canvas_2) 
        elif option == 4:
            afiseaza(get_channel(inv_matrix, 2), canvas_2)

def binarize(matrix, threshold=127):
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
                if V == r: H = 60*(g-b) / C
                elif V == g: H = 120 + 60*(b-r) / C
                elif V == b: H = 240 + 60*(r-g) / C
            if H < 0: H += 360
            if H >= 360: H -= 360

            # normalizare
            h_norm = H * 255/360
            s_norm = S * 255
            v_norm = V * 255
            new_row.append([h_norm, s_norm, v_norm])
        res.append(new_row)
    return res

def show_histogram(matrix):
    clear_analysis()
    hist = [0] * 256
    for row in matrix:
        for pixel in row:
            gray = int((pixel[0] + pixel[1] + pixel[2]) / 3)
            hist[gray] += 1
            
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.bar(range(256), hist, color='gray', width=1, edgecolor='none')
    ax.set_xlim(0, 255)

    canvas_mpl = FigureCanvasTkAgg(fig, master=frame_analysis)
    canvas_mpl.draw()
    canvas_mpl.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)

def clear_analysis():
    for widget in frame_analysis.winfo_children():
        widget.destroy()

def matrice_covarianta(mu20, mu02, mu11):
    cov = [
        [mu20, mu11],
        [mu11, mu02]
    ]
    print("\nMatricea de covarianta:")
    print(f"[ {mu20:.2f}   {mu11:.2f} ]")
    print(f"[ {mu11:.2f}   {mu02:.2f} ]")

    return cov

def calcul_momente_imagine(matrix):

    # ordin 1
    suma_intensitatii = 0
    sumax_intensitatii = 0
    sumay_intensitatii = 0
    for y, row in enumerate(matrix):
        for x, pixel in enumerate(row):
            r, g, b = pixel[0], pixel[1], pixel[2]
            intensitate = 0.299*r + 0.587*g + 0.114*b
            suma_intensitatii += intensitate
            sumax_intensitatii += x * intensitate
            sumay_intensitatii += y * intensitate
    
    m_x = sumax_intensitatii / suma_intensitatii
    m_y = sumay_intensitatii / suma_intensitatii
    return m_x, m_y

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
    MAX_W, MAX_H = 600, 600
    img.thumbnail((MAX_W, MAX_H))
    imgtk = ImageTk.PhotoImage(img)
    # canvas.config(width=img.width, height=img.height)
    canvas.create_image(300, 300, anchor="center", image=imgtk)
    canvas.image = imgtk

def center_window():
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2) - 50
    root.geometry(f"+{x}+{y}")

root = tk.Tk()
root.title("Photoshop aftermarket")
root.after(10, center_window)

# ================= MENIURI ====================
menubar = tk.Menu(root)
# fisier
menu_file = tk.Menu(menubar, tearoff=0)
menu_file.add_command(label="Deschide", command=open_image)
menu_file.add_command(label="Resetare", command=resetare)
menu_file.add_separator()
menu_file.add_command(label="Iesire", command=root.quit)
menubar.add_cascade(label="Fisier", menu=menu_file)

# conversii
menu_conversii = tk.Menu(menubar, tearoff=0)
menu_conversii.add_command(label="Gri - Media aritmetica", command=lambda: afiseaza(mod_gray(matrix, 1), canvas_2))
menu_conversii.add_command(label="Gri - Luminozitate", command=lambda: afiseaza(mod_gray(matrix, 2), canvas_2))
menu_conversii.add_command(label="Gri - Lightness", command=lambda: afiseaza(mod_gray(matrix, 3), canvas_2))
menu_conversii.add_separator()
menu_conversii.add_command(label="CMYK", command=lambda: afiseaza(convert_cmyk(matrix), canvas_2))
menu_conversii.add_command(label="YUV", command=lambda: afiseaza(convert_yuv(matrix), canvas_2))
menu_conversii.add_command(label="YCbCr", command=lambda: afiseaza(convert_yCbCr(matrix), canvas_2))
menu_conversii.add_command(label="HSV", command=lambda: afiseaza(convert_hsv(matrix), canvas_2))
menubar.add_cascade(label="Conversii", menu=menu_conversii)

# efecte
menu_efecte = tk.Menu(menubar, tearoff=0)
menu_efecte.add_command(label="Binarizare", command=lambda: afiseaza(binarize(matrix), canvas_2))
menu_inversare = tk.Menu(menu_efecte, tearoff=0)
menu_inversare.add_command(label="Afiseaza inversata", command=lambda: show_invert(1))
menu_inversare.add_command(label="Canal R", command=lambda: show_invert(2))
menu_inversare.add_command(label="Canal G", command=lambda: show_invert(3))
menu_inversare.add_command(label="Canal B", command=lambda: show_invert(4))

menu_efecte.add_cascade(label="Inversare", menu=menu_inversare)
menubar.add_cascade(label="Efecte", menu=menu_efecte)

# analiza
menu_analiza = tk.Menu(menubar, tearoff=0)
menu_analiza.add_command(label="Histograma", command=lambda: show_histogram(matrix))
menu_analiza.add_command(label="Momente", command=lambda: calcul_momente(binarize(matrix)))
menu_analiza.add_command(label="Proiectii", command=lambda: calcul_proiectii(binarize(matrix)))
menubar.add_cascade(label="Analiza", menu=menu_analiza)
root.config(menu=menubar)

frame_poze = tk.Frame(root)
frame_poze.pack()

canvas_original = tk.Canvas(frame_poze, width=600, height=600, bg="lightgray")
canvas_original.pack(side="left", padx=5, pady=5)

canvas_2 = tk.Canvas(frame_poze, width=600, height=600, bg="lightgray")
canvas_2.pack(side="left", padx=5, pady=5)

frame_analysis = tk.Frame(root, height=250, bg="#1e1e1e")
frame_analysis.pack(fill="x", padx=5, pady=5)
frame_analysis.pack_propagate(False)  # mentine inaltimea fixa chiar daca e gol

status_var = tk.StringVar(value="Niciun fisier deschis")

status_bar = tk.Label(root, textvariable=status_var, anchor="w")
status_bar.pack(fill="x", side="bottom")

root.mainloop()