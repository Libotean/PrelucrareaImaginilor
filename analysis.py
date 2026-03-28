import math

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
