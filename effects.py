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