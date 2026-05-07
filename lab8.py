from conversions import mod_gray
import math

def laplacian_filter(matrix):
    gray_matrix = mod_gray(matrix, method=2)
    height = len(gray_matrix)
    width = len(gray_matrix[0])

    res = [[[0,0,0] for _ in range(width)] for _ in range(height)]

    masca = [
        [-1, -1, -1],
        [-1, 8, -1],
        [-1, -1, -1]
    ]

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            sum = 0
            for n in range(-1, 2):
                for m in range(-1, 2):
                    pixel_val = gray_matrix[y + n][x + m][0]
                    sum += masca[n + 1][m + 1] * pixel_val
            final_val = max(0, min(255, int(sum)))
            res[y][x] = [final_val, final_val, final_val]
    return res

def remove_gaussian_noise(matrix):
    height = len(matrix)
    width = len(matrix[0])
    
    res = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]

    kernel_size = 3
    half_kernel = kernel_size // 2

    for y in range(height):
        for x in range(width):
            sum_r, sum_g, sum_b = 0, 0, 0
            for i in range(-half_kernel, half_kernel + 1):
                for j in range(-half_kernel, half_kernel + 1):
                    
                    offset_y = max(0, min(height - 1, y + i))
                    offset_x = max(0, min(width - 1, x + j))

                    pixel = matrix[offset_y][offset_x]
                    sum_r += pixel[0]
                    sum_g += pixel[1]
                    sum_b += pixel[2]

                num_pixels = kernel_size * kernel_size
                avg_r = sum_r // num_pixels
                avg_g = sum_g // num_pixels
                avg_b = sum_b // num_pixels

                res[y][x] = [avg_r, avg_g, avg_b]
    return res

def calculate_snr(matrix):
    height = len(matrix)
    width = len(matrix[0])

    signal_sum, noise_sum = 0, 0

    for row in matrix:
        for pixel in row:
            signal = pixel[0]
            noise = abs(255 - signal)

            signal_sum += signal
            noise_sum += noise

    total_pixels = width * height
    signal_mean = signal_sum / total_pixels
    noise_mean = noise_sum / total_pixels

    snr = 10 * math.log10((signal_mean**2) / (noise_mean**2))
    return snr

# def calculate_snr_2(matrix1, matrix2):
#     height = len(matrix1)
#     width = len(matrix1[0]) 

#     signal_sum, noise_sum = 0, 0

#     for y in range(height):
#         for x in range(width):
