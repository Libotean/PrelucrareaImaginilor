import math

def calcul_histograma(matrix):
    hist = [0] * 256
    for row in matrix:
        for pixel in row:
            gray = int((pixel[0] + pixel[1] + pixel[2]) / 3)
            hist[gray] += 1
    return hist

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
