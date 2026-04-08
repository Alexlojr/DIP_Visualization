import math
from pathlib import Path

from PIL import Image

from src.utils.paths import IMAGES_DIR


def binarization(image, threshold=127, on_progress=None):
    """Binarização manual sem NumPy/OpenCV"""
    if image is None: return None

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("L", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = width * height

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            new_pixels[x, y] = 255 if gray >= threshold else 0
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def grayscale(image, on_progress=None):
    """Conversão para escala de cinza manual (luminância ITU-R BT.601)"""
    if image is None: return None

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("L", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = width * height

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            new_pixels[x, y] = int(0.299 * r + 0.587 * g + 0.114 * b)
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def invert_colors(image, on_progress=None):
    """Negativo da imagem (inversão de cores)"""
    if image is None: return None

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = width * height

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            new_pixels[x, y] = (255 - r, 255 - g, 255 - b)
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def histogram_equalization(image, on_progress=None):
    """Equalização de histograma — melhora contraste redistribuindo intensidades"""
    if image is None: return None

    img = image.convert("L")
    width, height = img.size
    pixels = img.load()
    total = width * height

    hist = [0] * 256
    for x in range(width):
        for y in range(height):
            hist[pixels[x, y]] += 1

    cdf = [0] * 256
    cdf[0] = hist[0]
    for i in range(1, 256):
        cdf[i] = cdf[i - 1] + hist[i]

    cdf_min = next((c for c in cdf if c > 0), 0)
    denom = total - cdf_min
    if denom == 0:
        return img.copy()

    eq_map = [round((cdf[i] - cdf_min) / denom * 255) for i in range(256)]

    new_img = Image.new("L", (width, height))
    new_pixels = new_img.load()
    for x in range(width):
        for y in range(height):
            new_pixels[x, y] = eq_map[pixels[x, y]]
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def quantization(image, levels=8, on_progress=None):
    """Quantização de cores — reduz número de níveis de intensidade"""
    if image is None: return None

    levels = max(2, levels)
    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = width * height
    step = 256 // levels

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            new_pixels[x, y] = (
                min(255, (r // step) * step),
                min(255, (g // step) * step),
                min(255, (b // step) * step),
            )
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def brightness_adjust(image, value=30, on_progress=None):
    """Ajuste de brilho — soma/subtrai valor constante em cada canal"""
    if image is None: return None

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = width * height

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            new_pixels[x, y] = (
                min(255, max(0, r + value)),
                min(255, max(0, g + value)),
                min(255, max(0, b + value)),
            )
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def log_transform(image, c=45, on_progress=None):
    """Transformação logarítmica — realça detalhes em regiões escuras"""
    if image is None: return None

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = width * height

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            new_pixels[x, y] = (
                min(255, int(c * math.log(1 + r))),
                min(255, int(c * math.log(1 + g))),
                min(255, int(c * math.log(1 + b))),
            )
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def gamma_correction(image, gamma=1.0, on_progress=None):
    """Correção gama — ajusta brilho com curva de potência (γ<1 clareia, γ>1 escurece)"""
    if image is None: return None
    if gamma <= 0:
        gamma = 0.1

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = width * height

    lut = [min(255, int((i / 255) ** gamma * 255)) for i in range(256)]

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            new_pixels[x, y] = (lut[r], lut[g], lut[b])
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def apply_bw_mask(image, mask_path=None, on_progress=None):
    """
    Composição com máscara em tons de cinza: branco mantém o pixel da imagem;
    preto substitui por preto sólido (valores intermediários fazem blend linear).
    """
    if image is None:
        return None

    path = Path(mask_path) if mask_path is not None else IMAGES_DIR / "bw.png"
    try:
        mask_img = Image.open(path)
    except OSError as e:
        print(f"Erro ao abrir máscara {path}: {e}")
        return None

    base = image.convert("RGB")
    w, h = base.size
    total = w * h
    mask_L = mask_img.convert("L").resize(base.size, Image.Resampling.NEAREST)
    black = Image.new("RGB", base.size, (0, 0, 0))
    out = Image.composite(base, black, mask_L)

    if on_progress:
        on_progress(total, total)

    return out
