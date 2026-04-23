import math
import numpy as np

def calcul_histograma(matrix):
    """Calculeaza histograma de intensitate a unei imagini.
    Numara frecvente de aparitie a fiecarei nuante de gri din imagine.
    Foloseste media aritmetica simpla pentru conversia interna in grayscale.

    Args:
        matrix (list[list[list[int]]]): Imaginea sursa RGB.

    Returns:
        list[int]: O lista de 256 de elemente unde indexul reprezinta intensitatea, iar valoarea numarul de pixeli.
    """
    hist = [0] * 256
    for row in matrix:
        for pixel in row:
            gray = int((pixel[0] + pixel[1] + pixel[2]) / 3)
            hist[gray] += 1
    return hist

def calcul_momente_imagine(matrix):
    """Calculeaza momentele de ordin 1 si 2 ale imaginii.

    Args:
        matrix (list[list[list[int]]]): Imaginea sursa RGB.

    Returns:
        tuple: (m_x, m_y, M_xx, M_yy, M_xy, unghi_rad, unghi_grade)
            - m_x, m_y: coordonatele centrului de greutate.
            - M_xx, M_yy, M_xy: momentele de ordin 2.
            - unghi_rad/grade: orientarea axei principale a imaginii.
    """
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

    # ordin 2
    sumaxx = 0
    sumayy = 0
    sumaxy = 0
    for y,row in enumerate(matrix):
        for x, pixel in enumerate(row):
            r, g, b = pixel[0], pixel[1], pixel[2]
            intensitate = 0.299*r + 0.587*g + 0.114*b
            sumaxx += (x - m_x)**2 * intensitate
            sumayy += (y - m_y)**2 * intensitate
            sumaxy += (x - m_x) * (y - m_y) * intensitate

    M_xx = sumaxx / suma_intensitatii
    M_yy = sumayy / suma_intensitatii
    M_xy = sumaxy / suma_intensitatii
    unghi_rad = 0.5 * math.atan2(2 * M_xy, M_xx - M_yy)
    unghi_grade = math.degrees(unghi_rad)
    return m_x, m_y, M_xx, M_yy, M_xy, unghi_rad, unghi_grade

def calcul_proiectii(bin_matrix):  
    """Genereaza proiectiile pe axele orizontala si verticala ale unei imagini.
    Este utila pentru detectarea limitelor obiectelor sau segmentarea textului.

    Args:
        bin_matrix (list[list[list[int]]]): Imaginea binarizata.

    Returns:
        tuple: (proiectie_H, proiectie_V)
            - proiectie_H: Lista cu suma pixelilor albi pe fiecare rand.
            - proiectie_V: Lista cu suma pixelilor albi pe fiecare coloana. 
    """
    h = len(bin_matrix)
    w = len(bin_matrix[0])
    
    proiectie_H = [0] * h
    proiectie_V = [0] * w
    
    for y in range(h):
        for x in range(w):
            if bin_matrix[y][x][0] == 255:
                proiectie_H[y] += 1
                proiectie_V[x] += 1
    return proiectie_H, proiectie_V


def equalize_histogram(matrix, width, height):
    h = calcul_histograma(matrix)

    hc = [0] * 256
    hc[0] = h[0]
    for i in range(1, 256):
        hc[i] = hc[i-1] + h[i]

    hc_min = next((val for val in hc if val > 0), 0)
    total_pixeli = width * height
    
    new_pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            pixel = matrix[y][x]
            nivel_vechi = int((pixel[0] + pixel[1] + pixel[2]) / 3)
            
            if total_pixeli == hc_min:
                nivel_nou = nivel_vechi
            else:
                nivel_nou = int(((hc[nivel_vechi] - hc_min) / (total_pixeli - hc_min)) * 255)
            
            nivel_nou = max(0, min(255, nivel_nou))
            
            row.append([nivel_nou, nivel_nou, nivel_nou])
        new_pixels.append(row)
        
    return new_pixels

def apply_morphology(matrix, kernel, mode='dilate', iterations=1):
    if matrix is None:
        return None

    current_matrix = matrix
    height = len(matrix)
    width = len(matrix[0])
    
    k_rows = len(kernel)
    k_cols = len(kernel[0])
    offset_y = k_rows // 2
    offset_x = k_cols // 2

    for _ in range(iterations):
        new_matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                values = []
                for ky in range(k_rows):
                    for kx in range(k_cols):
                        if kernel[ky][kx] == 1:
                            iy = y + (ky - offset_y)
                            ix = x + (kx - offset_x)
                            
                            if 0 <= iy < height and 0 <= ix < width:
                                values.append(current_matrix[iy][ix][0])
                
                if not values:
                    row.append(current_matrix[y][x])
                    continue

                if mode == 'dilate':
                    res = max(values)
                else: 
                    res = min(values)
                
                row.append([res, res, res])
            new_matrix.append(row)
        current_matrix = new_matrix 
        
    return current_matrix

def opening(matrix, kernel, iterations=1):
    temp = apply_morphology(matrix, kernel, 'erode', iterations)
    return apply_morphology(temp, kernel, 'dilate', iterations)

def closing(matrix, kernel, iterations=1):
    temp = apply_morphology(matrix, kernel, 'dilate', iterations)
    return apply_morphology(temp, kernel, 'erode', iterations)

def apply_fourier(matrix):
    # daca ii fac un cerc in centru si ii aplic un filtru apoi ii dau reverse la fourier
    img_array = np.array([[p[0] for p in row] for row in matrix])
    f_transform = np.fft.fft2(img_array)
    
    f_shift = np.fft.fftshift(f_transform)
    
    magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1)
    
    min_val = np.min(magnitude_spectrum)
    max_val = np.max(magnitude_spectrum)
    if max_val > min_val:
        normalized = (magnitude_spectrum - min_val) * (255 / (max_val - min_val))
    else:
        normalized = magnitude_spectrum
    res_matrix = []
    for row in normalized:
        new_row = []
        for val in row:
            v = int(val)
            new_row.append([v, v, v])
        res_matrix.append(new_row)
        
    return res_matrix
