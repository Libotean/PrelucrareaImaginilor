def inversare(matrix):
    """Creeaza negativul unei imagini RGB. Inverteste culorile scazand valoarea fiecarui canal (R, G, B) din 255.

    Args:
        matrix (list[list[list[int]]]): Matricea imaginii sursa in format RGB.

    Returns:
        list[list[list[int]]]: O noua matrice reprezentand imaginea inversata.
    """
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            new_row.append([255 - pixel[0], 255 - pixel[1], 255 - pixel[2]])
        res.append(new_row)
    return res

def get_channel(matrix, channel='r'):
    """Extrage un canal de culoare specificat prin nume ('r', 'g', 'b').

    Args:
        matrix (list[list[list[int]]]): Matricea imaginii sursa.
        channel (int): Indexul canalului dorit: r pentru Rosu, g pentru Verde, b pentru Albastru.

    Returns:
        list[list[list[int]]]: Matricea imaginii continand doar canalul specificat.
    """
    mapping = {'r': 0, 'g': 1, 'b': 2}
    
    # validare input
    channel = channel.lower()
    if channel not in mapping:
        raise ValueError("Parametrul 'channel' trebuie sa fie 'r', 'g' sau 'b'.")
    
    idx = mapping[channel]
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            val = pixel[idx]
            new_pixel = [0, 0, 0]
            new_pixel[idx] = val
            new_row.append(new_pixel)
        res.append(new_row)
    return res

def binarize(matrix, threshold=127):
    """Converteste o imagine RGB (matrice) in format binar (alb-negru pur). 
    Transforma fiecare pixel in nunante de gri folosind formula luminantei, iar apoi aplica un prag
    pentru a decide daca pixelul devine alb sau negru.

    Args:
        matrix (list[list[list[int]]]): Matricea imaginii sursa in format RGB.
        threshold (int, optional): Valoarea limita pentru binarizare. Defaults to 127.

    Returns:
        list[list[list[int]]]: O noua matrice cu pixeli binarizati.
    """
    res = []
    for row in matrix:
        new_row = []
        for pixel in row:
            gray = int(0.299*pixel[0] + 0.587*pixel[1] + 0.114*pixel[2]) 
            if gray >= threshold:
                val = 255
            else: val = 0 
            new_row.append([val, val, val])
        res.append(new_row)
    return res