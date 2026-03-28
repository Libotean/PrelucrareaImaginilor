import struct

def read_bmp(file_path):
    """
    Citeste un fisier imagine BMP si extrage matricea de pixeli in format RGB.

    Funcsia parseaza structura binara a formatului BMP (Windows Bitmap), 
    suportand adâncimi de culoare de 4, 8, 16, 24 si 32 biti, precum si 
    imagini stocate Bottom-Up sau Top-Down.

    Args:
        file_path (str): Calea catre fisierul .bmp.

    Returns:
        tuple: (pixels, width, height, bit_count)
            - pixels: list[list[list[int]]] - Matricea de pixeli RGB.
            - width: int - Latimea imaginii.
            - height: int - Inaltimea imaginii.
            - bit_count: int - Adancimea de culoare detectata.

    Raises:
        ValueError: Daca fisierul nu este un BMP valid sau are un format nesuportat.
    """
    with open(file_path, 'rb') as f:
        file_header = f.read(14)
        if len(file_header) < 14:
            raise ValueError("File too small to be a BMP")
        if file_header[0:2] != b'BM':
            raise ValueError("Not a BMP file (invalid signature)")

        data_offset = struct.unpack('<I', file_header[10:14])[0]
        info_header = f.read(40)
        if len(info_header) < 40:
            raise ValueError("Incomplete BMP info header")

        width       = struct.unpack('<i', info_header[4:8])[0]
        height      = struct.unpack('<i', info_header[8:12])[0]
        bit_count   = struct.unpack('<H', info_header[14:16])[0]
        compression = struct.unpack('<I', info_header[16:20])[0]

        bottom_up  = height > 0
        abs_height = abs(height)

        palette = []
        if bit_count == 8:
            f.seek(14 + 40)
            for i in range(256):
                b, g, r, _ = f.read(4)
                palette.append([r, g, b])
        elif bit_count == 4:
            f.seek(14 + 40)
            for i in range(16):
                b, g, r, _ = f.read(4)
                palette.append([r, g, b])

        if bit_count == 24:
            row_size = ((width * 3 + 3) // 4) * 4
        elif bit_count == 32:
            row_size = width * 4
        elif bit_count == 8:
            row_size = ((width + 3) // 4) * 4
        elif bit_count == 4:
            row_size = ((width + 1) // 2 + 3) // 4 * 4
        elif bit_count == 16:
            row_size = ((width * 2 + 3) // 4) * 4
        else:
            raise ValueError(f"Unsupported bit count: {bit_count}")

        f.seek(data_offset)
        pixels = []
        for _ in range(abs_height):
            row_data = f.read(row_size)
            if len(row_data) < row_size:
                raise ValueError("Unexpected end of file")
            row_pixels = []
            if bit_count == 24:
                for x in range(width):
                    b = row_data[x * 3]
                    g = row_data[x * 3 + 1]
                    r = row_data[x * 3 + 2]
                    row_pixels.append([r, g, b])

            elif bit_count == 32:
                for x in range(width):
                    b = row_data[x * 4]
                    g = row_data[x * 4 + 1]
                    r = row_data[x * 4 + 2]
                    row_pixels.append([r, g, b])

            elif bit_count == 8:
                for x in range(width):
                    index = row_data[x]
                    row_pixels.append(palette[index])

            elif bit_count == 4:
                for x in range(width):
                    byte = row_data[x // 2]
                    if x % 2 == 0:
                        index = (byte >> 4) & 0x0F 
                    else:
                        index = byte & 0x0F
                    row_pixels.append(palette[index])

            elif bit_count == 16:
                for x in range(width):
                    pixel = struct.unpack('<H', row_data[x*2:x*2+2])[0]
                    if compression == 3: 
                        r = ((pixel >> 11) & 0x1F) * 255 // 31
                        g = ((pixel >> 5)  & 0x3F) * 255 // 63
                        b = ( pixel        & 0x1F) * 255 // 31
                    else: 
                        r = ((pixel >> 10) & 0x1F) * 255 // 31
                        g = ((pixel >> 5)  & 0x1F) * 255 // 31
                        b = ( pixel        & 0x1F) * 255 // 31
                    row_pixels.append([r, g, b])
                    
            pixels.append(row_pixels)

        if bottom_up:
            pixels.reverse()

        return pixels, width, abs_height, bit_count
