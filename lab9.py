import copy
import math
from conversions import mod_gray

def edge_detect(matrix, filter_type):
    FILTER_VERTICAL = [[1, 0, -1], [1, 0, -1], [1, 0, -1]] 
    FILTER_HORIZONTAL = [[1, 1, 1], [0, 0, 0], [-1, -1, -1]] 
    FILTER_SOBEL_V = [[1, 0, -1], [2, 0, -2], [1, 0, -1]] 
    FILTER_SOBEL_H = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]] 
    FILTER_SCHARR_V = [[3, 0, -3], [10, 0, -10], [3, 0, -3]] 
    FILTER_SCHARR_H = [[3, 10, 3], [0, 0, 0], [-3, -10, -3]]

    kernel = FILTER_SOBEL_V
    if filter_type == 1: kernel = FILTER_VERTICAL
    elif filter_type == 2: kernel = FILTER_HORIZONTAL
    elif filter_type == 3: kernel = FILTER_SOBEL_V
    elif filter_type == 4: kernel = FILTER_SOBEL_H
    elif filter_type == 5: kernel = FILTER_SCHARR_V
    elif filter_type == 6: kernel = FILTER_SCHARR_H

    height = len(matrix)
    width = len(matrix[0])

    red_ch, green_ch, blue_ch = [], [], []

    for row in matrix:
        red_row, green_row, blue_row = [], [], []
        for pixel in row:
            red_row.append(pixel[0])
            green_row.append(pixel[1])
            blue_row.append(pixel[2])
        red_ch.append(red_row)
        green_ch.append(green_row)
        blue_ch.append(blue_row)

    red_conv = convolution_type2(red_ch, height, width, kernel, 3, 3, 1)
    green_conv = convolution_type2(green_ch, height, width, kernel, 3, 3, 1)
    blue_conv = convolution_type2(blue_ch, height, width, kernel, 3, 3, 1)

    res = []
    for i in range(height):
        new_row = []
        for j in range(width):
            sum_val = red_conv[i][j] + green_conv[i][j] + blue_conv[i][j]
            gray = fix_out_of_rangeRGB(sum_val)
            new_row.append([gray, gray, gray])
        res.append(new_row)
    return res
    
def convolution_type2(image_channel, height, width, kernel, k_width, k_height, iterations):
    new_input = copy.deepcopy(image_channel)
    output = copy.deepcopy(image_channel)

    for i in range(iterations):
        output = convolution_2d_padded(new_input, height, width, kernel, k_width, k_height)
        new_input = copy.deepcopy(output)
    return output

def convolution_2d_padded(input_data, height, width, kernel, k_width, k_height):
    small_w = width - k_width + 1
    small_h = height - k_height + 1
    top = k_height // 2
    left = k_width // 2

    small = convolution_2d(input_data, height, width, kernel, k_width, k_height)
    large = []
    for i in range(height):
        row = [0.0] * width
        large.append(row)
    
    for j in range(small_h):
        for i in range(small_w):
            if (i + left) < width and (j + top) < height:
                large[j + top][i + left] = small[j][i]
    return large

def convolution_2d(input_data, height, width, kernel, k_width, k_height):
    small_w = width - k_width + 1
    small_h = height - k_height + 1

    output = []
    for i in range(small_h):
        row = [0.0] * small_w
        output.append(row)
    
    for j in range(small_h):
        for i in range(small_w):
            output[j][i] = single_pixel_convolution(input_data, i, j, kernel, k_width, k_height)
    return output

def single_pixel_convolution(input_data, x, y, kernel, k_width, k_height):
    output = 0.0
    for j in range(k_height):
        for i in range(k_width):
            output += input_data[y + j][x + i] * kernel[j][i]
    return output

def fix_out_of_rangeRGB(value):
    if value < 0:
        value = abs(value)
    if value > 255:
        return 255
    else:
        return int(value)
    
# Metoda Canny

def apply_canny_edge_detection(matrix):
    gray_image = mod_gray(matrix, 2)

    height = len(gray_image)
    width = len(gray_image[0])
    gray_2d = [[gray_image[y][x][0] for x in range(width)] for y in range(height)]

    blurred_image = apply_gaussian_blur(gray_2d)
    mag, angle = calculate_gradient(blurred_image)
    thinned_image = apply_non_maximum_suppression(mag, angle)
    detect_edges_image = apply_hysteresis_thresholding(thinned_image)
    
    res = []
    for y in range(height):
        row = []
        for x in range(width):
            val = detect_edges_image[y][x]
            row.append([val, val, val])
        res.append(row)
    return res

def apply_gaussian_blur(matrix):
    height = len(matrix)
    width = len(matrix[0])
    blurred = [[0 for _ in range(width)] for _ in range(height)]
    
    kernel = [
        [1,  4,  7,  4,  1],
        [4, 16, 26, 16,  4],
        [7, 26, 41, 26,  7],
        [4, 16, 26, 16,  4],
        [1,  4,  7,  4,  1]
    ]
    kernel_sum = 273.0

    for y in range(2, height - 2):
        for x in range(2, width - 2):
            sum_val = 0
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    sum_val += matrix[y + dy][x + dx] * kernel[dy + 2][dx + 2]
            blurred[y][x] = int(sum_val / kernel_sum)
    return blurred

def calculate_gradient(matrix):
    height = len(matrix)
    width = len(matrix[0])
    mag = [[0.0 for _ in range(width)] for _ in range(height)]
    angle = [[0.0 for _ in range(width)] for _ in range(height)]

    gx_k = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    gy_k = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            gx = 0
            gy = 0
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    pixel = matrix[y + dy][x + dx]
                    gx += pixel * gx_k[dy + 1][dx + 1]
                    gy += pixel * gy_k[dy + 1][dx + 1]
            
            mag[y][x] = math.sqrt(gx**2 + gy**2)
            angle[y][x] = math.atan2(gy, gx)
    return mag, angle

def apply_non_maximum_suppression(mag, angle_matrix):
    height = len(mag)
    width = len(mag[0])
    thinned = [[0 for _ in range(width)] for _ in range(height)]

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            theta = math.degrees(angle_matrix[y][x]) % 180
            if theta < 0: theta += 180

            pixel1, pixel2 = 255, 255

            if (0 <= theta < 22.5) or (157.5 <= theta <= 180):
                pixel1 = mag[y][x - 1]
                pixel2 = mag[y][x + 1]
            elif (22.5 <= theta < 67.5):
                pixel1 = mag[y - 1][x + 1]
                pixel2 = mag[y + 1][x - 1]
            elif (67.5 <= theta < 112.5):
                pixel1 = mag[y - 1][x]
                pixel2 = mag[y + 1][x]
            else:
                pixel1 = mag[y - 1][x - 1]
                pixel2 = mag[y + 1][x + 1]

            if mag[y][x] >= pixel1 and mag[y][x] >= pixel2:
                thinned[y][x] = int(mag[y][x])
            else:
                thinned[y][x] = 0
    return thinned

def apply_hysteresis_thresholding(input_matrix):
    UPPER_THRESHOLD = 150
    LOWER_THRESHOLD = 50
    height = len(input_matrix)
    width = len(input_matrix[0])
    res = [[0 for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            intensity = input_matrix[y][x]
            
            if intensity > UPPER_THRESHOLD:
                res[y][x] = 255
            elif intensity < LOWER_THRESHOLD:
                res[y][x] = 0 
            else:
                if check_neighbours(input_matrix, x, y, UPPER_THRESHOLD):
                    res[y][x] = 255
                else:
                    res[y][x] = 0
    return res

def check_neighbours(matrix, x, y, threshold):
    height = len(matrix)
    width = len(matrix[0])
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if matrix[ny][nx] > threshold:
                    return True
    return False