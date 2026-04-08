import math
from pathlib import Path

from PIL import Image

from src.utils.paths import IMAGES_DIR


def binarization(image, threshold=127, on_progress=None):
    """Manual binarization without NumPy/OpenCV."""
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
    """Manual grayscale conversion (ITU-R BT.601 luminance)."""
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
    """Image negative (color inversion)."""
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
    """Histogram equalization to improve contrast by redistributing intensities."""
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
    """Color quantization - reduces the number of intensity levels."""
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
    """Brightness adjustment - add/subtract a constant per channel."""
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
    """Log transform - enhances details in darker regions."""
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
    """Gamma correction using a power curve (gamma<1 brightens, gamma>1 darkens)."""
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
    Grayscale mask composition: white keeps the original pixel;
    black replaces it with solid black (intermediate values use m/255 scaling).

    Explicit implementation: mask luminance (BT.601), integer nearest-neighbor
    resizing, and per-pixel blending - no Image.composite/Image.resize.
    """
    if image is None:
        return None

    path = Path(mask_path) if mask_path is not None else IMAGES_DIR / "bw.png"
    try:
        mask_img = Image.open(path)
    except OSError as e:
        print(f"Error opening mask {path}: {e}")
        return None

    base = image.convert("RGB")
    w, h = base.size
    total = w * h
    bp = base.load()

    mask_rgb = mask_img.convert("RGB")
    mw, mh = mask_rgb.size
    mp = mask_rgb.load()
    # Grayscale mask via luminance (same weights used by this module)
    mask_vals = [0] * (mw * mh)
    i = 0
    for my in range(mh):
        for mx in range(mw):
            r, g, b = mp[mx, my]
            mask_vals[i] = int(0.299 * r + 0.587 * g + 0.114 * b)
            i += 1

    new_img = Image.new("RGB", (w, h))
    npix = new_img.load()

    for x in range(w):
        # Nearest-neighbor: output (x, y) -> source index in mw x mh mask
        sx = (x * mw) // w if w else 0
        for y in range(h):
            sy = (y * mh) // h if h else 0
            m = mask_vals[sy * mw + sx]
            r, g, b = bp[x, y]
            npix[x, y] = (r * m // 255, g * m // 255, b * m // 255)
        if on_progress:
            on_progress((x + 1) * h, total)

    return new_img
