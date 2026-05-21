import math
from conversions import mod_gray

def apply_laplacian_of_Gaussian(matrix):
    smoothed_img = apply_Gaussian_filter(matrix, 3, 1.4);
    laplacian_img = apply_Laplace_filter(smoothed_img);
    return laplacian_img

def apply_Gaussian_filter(matrix, kernel_size, sigma):
    half_size = kernel_size // 2
    kernel = [[0.0] * kernel_size for _ in range(kernel_size)]
    kernelSum = 0.0

    for i in range(-half_size, half_size +1):
        for j in range(-half_size, half_size + 1):
            value = math.exp(-(i*i + j*j) / (2 * sigma * sigma))
            kernel[i + half_size][j + half_size] = value
            kernelSum += value
    
    for i in range(kernel_size):
        for j in range(kernel_size):
            kernel[i][j] /= kernelSum

    return apply_convolution(matrix, kernel)

def apply_convolution(matrix, kernel):
    width = len(matrix[0])
    height = len(matrix) 
    output_image = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    kernel_size = len(kernel)
    half_size = kernel_size // 2

    for y in range(half_size, height - half_size):
        for x in range(half_size, width - half_size):
            sum = 0.0
            for i in range(-half_size, half_size + 1):
                for j in range(-half_size, half_size + 1):
                    neightbor_pixel = matrix[y + i][x + j]
                    pixel_value = neightbor_pixel[0]

                    kernel_value = kernel[i + half_size][j + half_size]
                    sum += pixel_value * kernel_value
            new_value = int(round(sum))
            new_value = min(255, max(0, new_value))
            # print(new_value)
            # if new_value > 200:
            #     new_value = 0
            # elif new_value < 0:
            #     new_value = 255
            output_image[y][x] = [new_value, new_value, new_value]
            # output_image[y][x] = [255, 0, new_value]
    return output_image

def apply_Laplace_filter(matrix):
    laplace_kernel = [
        [-1, -1, -1],
        [-1, 8, -1],
        [-1, -1, -1],
    ]
    return apply_convolution(matrix, laplace_kernel)

    