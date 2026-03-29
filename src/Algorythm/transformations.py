from PIL import Image, ImageFilter


def rotate_90cw(image, on_progress=None):
    """Placeholder — Rotação 90° horário."""
    print("rotate_90cw: not implemented")
    return image.copy() if image else None


def rotate_90ccw(image, on_progress=None):
    """Placeholder — Rotação 90° anti-horário."""
    print("rotate_90ccw: not implemented")
    return image.copy() if image else None


def rotate_180(image, on_progress=None):
    """Placeholder — Rotação 180°."""
    print("rotate_180: not implemented")
    return image.copy() if image else None


def rotate_free(image, angle=45, on_progress=None):
    """Placeholder — Rotação em ângulo livre (graus)."""
    print(f"rotate_free: not implemented (angle={angle})")
    return image.copy() if image else None


def flip_horizontal(image, on_progress=None):
    """Placeholder — Espelhamento horizontal."""
    print("flip_horizontal: not implemented")
    return image.copy() if image else None


def flip_vertical(image, on_progress=None):
    """Placeholder — Espelhamento vertical."""
    print("flip_vertical: not implemented")
    return image.copy() if image else None


def upscale(image, factor=2, on_progress=None):
    """
    Aumenta a resolução de imagens de baixa qualidade (thumbs, etc).

    Pipeline:
    1. cv2.resize com INTER_LANCZOS4 — melhor interpolação do OpenCV para upscaling
    2. Unsharp mask com NumPy — subtrai versão borrada (Gaussian blur) da imagem
       escalada para recuperar nitidez nas bordas sem criar halos artificiais

    factor: multiplicador de tamanho (2 = dobro, 3 = triplo, etc.)
    """
    if image is None:
        return None

    import cv2
    import numpy as np

    factor = max(2, factor)
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb)

    # BGR para OpenCV
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    h, w = bgr.shape[:2]
    upscaled = cv2.resize(bgr, (w * factor, h * factor), interpolation=cv2.INTER_LANCZOS4)

    # Unsharp mask: original - gaussian_blur devolve as frequências altas (bordas/detalhes)
    blurred = cv2.GaussianBlur(upscaled, (0, 0), sigmaX=1.5)
    sharpened = cv2.addWeighted(upscaled, 1.5, blurred, -0.5, 0)

    result_rgb = cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB)
    print(f"Upscale: {w}×{h} → {w*factor}×{h*factor} (×{factor}, LANCZOS4 + unsharp mask)")
    return Image.fromarray(result_rgb)
