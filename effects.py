import numpy as np

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

def apply_neighbor_filter(matrix, filter_type='mean'):
    height = len(matrix)
    width = len(matrix[0])
    new_matrix = [ [[0,0,0] for _ in range(width)] for _ in range(height)]

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            neighbors = []
            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    neighbors.append(matrix[y + ky][x + kx][0])
            
            if filter_type == 'mean':
                res = sum(neighbors) // 9
            elif filter_type == 'median':
                neighbors.sort()
                res = neighbors[4]
            elif filter_type == 'min':
                res = min(neighbors)
            elif filter_type == 'max':
                res = max(neighbors)
            
            new_matrix[y][x] = [res, res, res]
            
    return new_matrix

def apply_sharpen(matrix):
    height = len(matrix)
    width = len(matrix[0])
    new_matrix = [ [[0,0,0] for _ in range(width)] for _ in range(height)]
    
    v = [
        [0, -0.25, 0],
        [-0.25, 1, -0.25],
        [0, -0.25, 0]
    ]
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            sum_r = 0
            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    sum_r += v[ky+1][kx+1] * matrix[y+ky][x+kx][0]
            
            orig_r = matrix[y][x][0]
            new_r = int(orig_r + 0.6 * sum_r)
            
            new_r = max(0, min(255, new_r))
            new_matrix[y][x] = [new_r, new_r, new_r]
            
    return new_matrix

def apply_neighbor_filter_color(matrix, filter_type='mean'):
    height = len(matrix)
    width = len(matrix[0])
    new_matrix = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            new_pixel = [0, 0, 0]
            
            for c in range(3):
                neighbors = []
                for ky in range(-1, 2):
                    for kx in range(-1, 2):
                        neighbors.append(matrix[y + ky][x + kx][c])
                
                if filter_type == 'mean':
                    res = sum(neighbors) // 9
                elif filter_type == 'median':
                    neighbors.sort()
                    res = neighbors[4]
                elif filter_type == 'min':
                    res = min(neighbors)
                elif filter_type == 'max':
                    res = max(neighbors)
                
                new_pixel[c] = res
            
            new_matrix[y][x] = new_pixel
            
    return new_matrix

def apply_sharpen_color(matrix):
    height = len(matrix)
    width = len(matrix[0])
    new_matrix = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    
    v = [
        [0, -0.25, 0],
        [-0.25, 1, -0.25],
        [0, -0.25, 0]
    ]
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            new_pixel = [0, 0, 0]
            
            for c in range(3):
                sum_val = 0
                for ky in range(-1, 2):
                    for kx in range(-1, 2):
                        sum_val += v[ky+1][kx+1] * matrix[y+ky][x+kx][c]
                
                orig_val = matrix[y][x][c]
                res = int(orig_val + 0.6 * sum_val)
                
                new_pixel[c] = max(0, min(255, res))
            
            new_matrix[y][x] = new_pixel
            
    return new_matrix

def apply_floyd_steinberg(matrix):
    work_matrix = np.array(matrix, dtype=float)
    height, width, _ = work_matrix.shape

    for y in range(height):
        for x in range(width):
            for c in range(3):
                old_pixel = work_matrix[y, x, c]
                new_pixel = 255 if old_pixel > 127 else 0
                work_matrix[y, x, c] = new_pixel
                
                error = old_pixel - new_pixel
                
                if x + 1 < width:
                    work_matrix[y, x + 1, c] += error * 7 / 16
                if y + 1 < height:
                    if x - 1 >= 0:
                        work_matrix[y + 1, x - 1, c] += error * 3 / 16
                    work_matrix[y + 1, x, c] += error * 5 / 16
                    if x + 1 < width:
                        work_matrix[y + 1, x + 1, c] += error * 1 / 16

    return work_matrix.clip(0, 255).astype(np.uint8).tolist()