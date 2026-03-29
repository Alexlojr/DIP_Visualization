import math
from PIL import Image


# ---------------------------------------------------------------------------
# Passa Baixa (suavização)
# ---------------------------------------------------------------------------

def mean_filter(image, kernel_size=3, on_progress=None):
    """Filtro de média — suaviza a imagem calculando a média dos vizinhos"""
    if image is None: return None
    if kernel_size % 2 == 0:
        kernel_size += 1

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    indexer = kernel_size // 2
    total = width * height

    for x in range(width):
        for y in range(height):
            r_sum = g_sum = b_sum = count = 0
            for i in range(x - indexer, x + indexer + 1):
                for j in range(y - indexer, y + indexer + 1):
                    if 0 <= i < width and 0 <= j < height:
                        r, g, b = pixels[i, j]
                        r_sum += r; g_sum += g; b_sum += b
                        count += 1
            new_pixels[x, y] = (r_sum // count, g_sum // count, b_sum // count)
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def median_filter(image, kernel_size=3, on_progress=None):
    """Filtro de mediana — remove ruído sal-e-pimenta preservando bordas"""
    if image is None: return None
    if kernel_size % 2 == 0:
        kernel_size += 1

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    indexer = kernel_size // 2
    total = width * height

    for x in range(width):
        for y in range(height):
            r_vals, g_vals, b_vals = [], [], []
            for i in range(x - indexer, x + indexer + 1):
                for j in range(y - indexer, y + indexer + 1):
                    if 0 <= i < width and 0 <= j < height:
                        r, g, b = pixels[i, j]
                        r_vals.append(r); g_vals.append(g); b_vals.append(b)
            r_vals.sort(); g_vals.sort(); b_vals.sort()
            mid = len(r_vals) // 2
            new_pixels[x, y] = (r_vals[mid], g_vals[mid], b_vals[mid])
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def gaussian_filter(image, kernel_size=5, on_progress=None):
    """Filtro gaussiano — suavização com pesos maiores no centro do kernel"""
    if image is None: return None
    if kernel_size % 2 == 0:
        kernel_size += 1

    sigma = kernel_size / 3.0
    center = kernel_size // 2

    total_w = 0.0
    kernel = []
    for i in range(kernel_size):
        row = []
        for j in range(kernel_size):
            dx = i - center; dy = j - center
            val = math.exp(-(dx * dx + dy * dy) / (2 * sigma * sigma))
            row.append(val)
            total_w += val
        kernel.append(row)
    kernel = [[v / total_w for v in row] for row in kernel]

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = width * height

    for x in range(width):
        for y in range(height):
            r_sum = g_sum = b_sum = w_sum = 0.0
            for i in range(kernel_size):
                for j in range(kernel_size):
                    pi = x - center + i; pj = y - center + j
                    if 0 <= pi < width and 0 <= pj < height:
                        r, g, b = pixels[pi, pj]
                        w = kernel[i][j]
                        r_sum += r * w; g_sum += g * w; b_sum += b * w
                        w_sum += w
            if w_sum > 0:
                new_pixels[x, y] = (int(r_sum / w_sum), int(g_sum / w_sum), int(b_sum / w_sum))
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


# ---------------------------------------------------------------------------
# Passa Alta (realce de bordas)
# ---------------------------------------------------------------------------

def sobel_filter(image, on_progress=None):
    """Filtro Sobel — detecta bordas calculando gradiente nas direções X e Y"""
    if image is None: return None

    img = image.convert("L")
    width, height = img.size
    new_img = Image.new("L", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    Gy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    total = (width - 2) * (height - 2)

    for x in range(1, width - 1):
        for y in range(1, height - 1):
            gx = gy = 0
            for i in range(3):
                for j in range(3):
                    px = pixels[x - 1 + i, y - 1 + j]
                    gx += Gx[i][j] * px; gy += Gy[i][j] * px
            new_pixels[x, y] = min(255, int(math.sqrt(gx * gx + gy * gy)))
        if on_progress:
            on_progress((x) * (height - 2), total)

    return new_img


def laplacian_filter(image, on_progress=None):
    """Filtro Laplaciano — realça bordas usando derivada segunda da intensidade"""
    if image is None: return None

    img = image.convert("L")
    width, height = img.size
    new_img = Image.new("L", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    kernel = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    total = (width - 2) * (height - 2)

    for x in range(1, width - 1):
        for y in range(1, height - 1):
            val = 0
            for i in range(3):
                for j in range(3):
                    val += kernel[i][j] * pixels[x - 1 + i, y - 1 + j]
            new_pixels[x, y] = min(255, max(0, abs(val)))
        if on_progress:
            on_progress((x) * (height - 2), total)

    return new_img


def prewitt_filter(image, on_progress=None):
    """Filtro Prewitt — detecta bordas similar ao Sobel, pesos uniformes"""
    if image is None: return None

    img = image.convert("L")
    width, height = img.size
    new_img = Image.new("L", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    Gx = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
    Gy = [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
    total = (width - 2) * (height - 2)

    for x in range(1, width - 1):
        for y in range(1, height - 1):
            gx = gy = 0
            for i in range(3):
                for j in range(3):
                    px = pixels[x - 1 + i, y - 1 + j]
                    gx += Gx[i][j] * px; gy += Gy[i][j] * px
            new_pixels[x, y] = min(255, int(math.sqrt(gx * gx + gy * gy)))
        if on_progress:
            on_progress((x) * (height - 2), total)

    return new_img


def sharpen_filter(image, on_progress=None):
    """Aguçamento (sharpening) — realça detalhes subtraindo versão suavizada"""
    if image is None: return None

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    kernel = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
    total = (width - 2) * (height - 2)

    for x in range(1, width - 1):
        for y in range(1, height - 1):
            r_val = g_val = b_val = 0
            for i in range(3):
                for j in range(3):
                    r, g, b = pixels[x - 1 + i, y - 1 + j]
                    k = kernel[i][j]
                    r_val += k * r; g_val += k * g; b_val += k * b
            new_pixels[x, y] = (
                min(255, max(0, r_val)),
                min(255, max(0, g_val)),
                min(255, max(0, b_val)),
            )
        if on_progress:
            on_progress((x) * (height - 2), total)

    for x in range(width):
        new_pixels[x, 0] = pixels[x, 0]
        new_pixels[x, height - 1] = pixels[x, height - 1]
    for y in range(height):
        new_pixels[0, y] = pixels[0, y]
        new_pixels[width - 1, y] = pixels[width - 1, y]

    return new_img
