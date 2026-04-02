from collections import deque
import math

CULORI = [
    (255, 0,   0  ),  # rosu
    (0,   255, 0  ),  # verde
    (0,   0,   255),  # albastru
    (255, 255, 0  ),  # galben
    (255, 0,   255),  # magenta
    (0,   255, 255),  # cyan
    (255, 128, 0  ),  # portocaliu
    (128, 0,   255),  # mov
    (0,   255, 128),  # verde-cyan
    (255, 0,   128),  # roz
]

def gray(pixel):
    return int((pixel[0] + pixel[1] + pixel[2]) / 3)

def directie_alungire(matrix):
    height = len(matrix)
    width = len(matrix[0])
    gradientX = [[0.0] * width for _ in range(height)]
    gradientY = [[0.0] * width for _ in range(height)]
    for y, row in enumerate(matrix):
        for x, pixel in enumerate(row):
            if x == 0 or y == 0 or x == len(row)-1 or y == len(matrix)-1:
                gradientX[y][x] = 0
                gradientY[y][x] = 0
                continue

            p_top_left  = gray(matrix[y-1][x-1])
            p_top       = gray(matrix[y-1][x  ])
            p_top_right = gray(matrix[y-1][x+1])
            p_mid_left  = gray(matrix[y  ][x-1])
            p_mid_right = gray(matrix[y  ][x+1])
            p_bot_left  = gray(matrix[y+1][x-1])
            p_bot       = gray(matrix[y+1][x  ])
            p_bot_right = gray(matrix[y+1][x+1])

            gradientX[y][x] = p_top_right + 2*p_mid_right + p_bot_right - (p_top_left + 2*p_mid_left + p_bot_left)
            gradientY[y][x] = p_bot_left + 2*p_bot + p_bot_right - (p_top_left + 2*p_top + p_top_right)
    
    max_magnitude = 0.0
    orientation = 0.0

    for y, row in enumerate(gradientX):
        for x, gx in enumerate(row):
            gy = gradientY[y][x]
            magnitude = math.sqrt(gx * gx + gy * gy)

            if magnitude > max_magnitude:
                max_magnitude = magnitude
                orientation = math.atan2(gy, gx)

    return orientation, math.degrees(orientation)

def etichetare(matrix):
    height = len(matrix)
    width  = len(matrix[0])

    labels = [[0] * width for _ in range(height)]
    label  = 0

    for y in range(height):
        for x in range(width):

            if gray(matrix[y][x]) < 128 and labels[y][x] == 0:
                label += 1
                labels[y][x] = label

                queue = deque()
                queue.append((y, x))

                while queue:
                    cy, cx = queue.popleft()

                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0:
                                continue

                            ny = cy + dy
                            nx = cx + dx

                            if 0 <= ny < height and 0 <= nx < width:
                                if gray(matrix[ny][nx]) < 128 and labels[ny][nx] == 0:
                                    labels[ny][nx] = label
                                    queue.append((ny, nx))

    num_labels = label

    imagine_colorata = [[[255, 255, 255] for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            eticheta = labels[y][x]
            if eticheta > 0:
                culoare = CULORI[(eticheta - 1) % len(CULORI)]
                imagine_colorata[y][x] = list(culoare)

    return imagine_colorata, labels, num_labels

def extrage_obiect(matrix, labels, eticheta_selectata):
    height = len(matrix)
    width  = len(matrix[0])

    rezultat = [[[255, 255, 255] for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            if labels[y][x] == eticheta_selectata:
                rezultat[y][x] = list(matrix[y][x])

    return rezultat
