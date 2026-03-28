def mod_gray(matrix, method):
    """Transforma o imagine RGB in nunante de gri folosind trei metode diferite.

    Args:
        matrix (list[list[list[int]]]): Imaginea sursa RGB.
        method (int): Selector pentru algoritm:
            1 - Media aritmetica simpla.
            2 - Metoda luminantei - conform perceptiei umane.
            3 - Metoda desaturarii - media dintre min si max.

    Returns:
        list[list[list[int]]]: Imaginea in nuante de gri (R=G=B).
    """
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
    """Converteste o imagine din spatiul de culoare RGB in CMY.

    Args:
        matrix (list[list[list[int]]]): Imaginea sursa RGB.

    Returns:
        list[list[list[int]]]: Imaginea convertita.
    """
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
    """Converteste imaginea din spatiul de culoare RGB in YUV.
    Y reprezinta luminanta, iar U si V reprezinta crominanta. 
    Valorile U si V sunt shiftate cu +128 pentru a fi reprezentate in intervalul [0, 255].

    Args:
        matrix (list[list[list[int]]]): Imaginea sursa RGB.

    Returns:
        list[list[list[int]]]: Imaginea in format YUV (Y, U+128, V+128).
    """
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            r, g, b = pixel[0], pixel[1], pixel[2]
            y = 0.3*r + 0.6*g + 0.1*b 
            u = 0.74*(r-y) + 0.27*(b-y)
            v = 0.48*(r-y) + 0.41*(b-y)
            new_row.append([
                int(max(0, min(255, y))),
                int(max(0, min(255, u + 128))),
                int(max(0, min(255, v + 128)))
            ])
        res.append(new_row)
    return res

def convert_yCbCr(matrix):
    """Converteste imaginea in spatiul YCbCr.

    Args:
        matrix (list[list[list[int]]]): Imaginea sursa RGB.

    Returns:
        list[list[list[int]]]: Imaginea convertita.
    """
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

def convert_hsv(matrix):
    """Converteste imaginea din RGB in spatiul HSV (Hue, Saturation, Value).

    Args:
        matrix (list[list[list[int]]]): Imaginea sursa RGB.

    Returns:
        list[list[list[int]]]: Imaginea HSV cu valorile normalizate la intervalul [0, 255].
    """
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            r, g, b = pixel[0]/255.0, pixel[1]/255.0, pixel[2]/255.0
            M = max(r,g,b)
            m = min(r,g,b)
            C = M-m

            # value
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