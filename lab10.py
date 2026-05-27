import math
import struct
from conversions import mod_gray

def apply_laplacian_of_Gaussian(matrix):
    smoothed_img = apply_Gaussian_filter(matrix, 3, 1.4);
    laplacian_img = apply_Laplace_filter(smoothed_img);
    return laplacian_img

def apply_Gaussian_filter(matrix, kernel_size, sigma):
    half_size = kernel_size // 2
    kernel = [[0.0] * kernel_size for _ in range(kernel_size)]
    kernelSum = 0.0

    for i in range(-half_size, half_size +1):
        for j in range(-half_size, half_size + 1):
            value = math.exp(-(i*i + j*j) / (2 * sigma * sigma))
            kernel[i + half_size][j + half_size] = value
            kernelSum += value
    
    for i in range(kernel_size):
        for j in range(kernel_size):
            kernel[i][j] /= kernelSum

    return apply_convolution(matrix, kernel)

def apply_convolution(matrix, kernel):
    width = len(matrix[0])
    height = len(matrix) 
    output_image = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    kernel_size = len(kernel)
    half_size = kernel_size // 2

    for y in range(half_size, height - half_size):
        for x in range(half_size, width - half_size):
            sum = 0.0
            for i in range(-half_size, half_size + 1):
                for j in range(-half_size, half_size + 1):
                    neightbor_pixel = matrix[y + i][x + j]
                    pixel_value = neightbor_pixel[0]

                    kernel_value = kernel[i + half_size][j + half_size]
                    sum += pixel_value * kernel_value
            new_value = int(round(sum))
            new_value = min(255, max(0, new_value))
            # print(new_value)
            # if new_value > 200:
            #     new_value = 0
            # elif new_value < 0:
            #     new_value = 255
            output_image[y][x] = [new_value, new_value, new_value]
            # output_image[y][x] = [255, 0, new_value]
    return output_image

def apply_Laplace_filter(matrix):
    laplace_kernel = [
        [-1, -1, -1],
        [-1, 8, -1],
        [-1, -1, -1],
    ]
    return apply_convolution(matrix, laplace_kernel)


def lzw_comprimare(octeti_plati):
    dict_size = 256
    string_table = {chr(i): i for i in range(dict_size)}
    
    P = ""
    coduri = []
    
    for valoare_octet in octeti_plati:
        C = chr(valoare_octet)
        PC = P + C
        
        if PC in string_table:
            P = PC
        else:
            coduri.append(string_table[P])
            if dict_size < 65535:
                string_table[PC] = dict_size
                dict_size += 1
            P = C
            
    if P:
        coduri.append(string_table[P])
        
    return coduri

def lzw_decomprimare(coduri_comprimate):
    if not coduri_comprimate:
        return bytearray()
        
    dict_size = 256
    string_table = {i: chr(i) for i in range(dict_size)}
    
    OLD = coduri_comprimate[0]
    S = string_table[OLD]
    
    text_decomprimat = S
    C = S[0]
    
    for NEW in coduri_comprimate[1:]:
        if NEW not in string_table:
            S = string_table[OLD] + C
        else:
            S = string_table[NEW]
            
        text_decomprimat += S
        C = S[0]
        
        if dict_size < 65535:
            string_table[dict_size] = string_table[OLD] + C
            dict_size += 1
            
        OLD = NEW
        
    octeti_plati = bytearray()
    for caracter in text_decomprimat:
        octeti_plati.append(ord(caracter))
        
    return octeti_plati

def salveaza_imagine_lzw(cale_fisier, pixeli):
    inaltime = len(pixeli)
    latime = len(pixeli[0]) if inaltime > 0 else 0
    
    octeti_plati = bytearray()
    for rand in pixeli:
        for pixel in rand:
            octeti_plati.extend(pixel) 
            
    coduri = lzw_comprimare(octeti_plati)
    
    with open(cale_fisier, 'wb') as f:
        f.write(struct.pack('<II', latime, inaltime))
        for cod in coduri:
            f.write(struct.pack('<H', cod))
            
    print(f"Imaginea a fost salvata cu succes in {cale_fisier}")

def incarca_imagine_lzw(cale_fisier):
    with open(cale_fisier, 'rb') as f:
        antet = f.read(8)
        if len(antet) < 8:
            raise ValueError("Fisierul .lzw este corupt sau incomplet.")
            
        latime, inaltime = struct.unpack('<II', antet)
        
        coduri_comprimate = []
        while True:
            octeti_cod = f.read(2)
            if not octeti_cod:
                break
            cod = struct.unpack('<H', octeti_cod)[0]
            coduri_comprimate.append(cod)
            
    octeti_plati = lzw_decomprimare(coduri_comprimate)
    
    pixeli = []
    index = 0
    for y in range(inaltime):
        rand_pixeli = []
        for x in range(latime):
            r = octeti_plati[index]
            g = octeti_plati[index+1]
            b = octeti_plati[index+2]
            rand_pixeli.append([r, g, b])
            index += 3
        pixeli.append(rand_pixeli)
        
    return pixeli
    