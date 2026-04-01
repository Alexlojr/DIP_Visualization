from PIL import Image, ImageFilter


def rotate_90cw(image, on_progress=None):
    """
    Rotação 90° horário — sem numpy/opencv.

    Mapeamento: pixel src(x, y) → dst(H-1-y, x)
    Inverso:    dst(out_x, out_y) = src(out_y, H-1-out_x)
    Tamanho de saída: (H, W)  [largura e altura trocam]

    Pixels armazenados em lista plana, ordem row-major:
        índice = y * largura + x
    """
    if image is None:
        return None

    img = image.convert("RGB")
    W, H = img.size
    pixels = list(img.getdata())
    total = W * H
    out_pixels = []

    for out_y in range(W):          # nova altura = W original
        for out_x in range(H):      # nova largura = H original
            out_pixels.append(pixels[(H - 1 - out_x) * W + out_y])
        if on_progress:
            on_progress((out_y + 1) * H, total)

    out = Image.new("RGB", (H, W))
    out.putdata(out_pixels)
    return out


def rotate_90ccw(image, on_progress=None):
    """
    Rotação 90° anti-horário — sem numpy/opencv.

    Mapeamento: pixel src(x, y) → dst(y, W-1-x)
    Inverso:    dst(out_x, out_y) = src(W-1-out_y, out_x)
    Tamanho de saída: (H, W)
    """
    if image is None:
        return None

    img = image.convert("RGB")
    W, H = img.size
    pixels = list(img.getdata())
    total = W * H
    out_pixels = []

    for out_y in range(W):          # nova altura = W original
        for out_x in range(H):      # nova largura = H original
            out_pixels.append(pixels[out_x * W + (W - 1 - out_y)])
        if on_progress:
            on_progress((out_y + 1) * H, total)

    out = Image.new("RGB", (H, W))
    out.putdata(out_pixels)
    return out


def rotate_180(image, on_progress=None):
    """
    Rotação 180° — sem numpy/opencv.

    Mapeamento: pixel src(x, y) → dst(W-1-x, H-1-y)
    Equivalente a inverter a lista plana completa.
    Tamanho de saída: igual ao original.
    """
    if image is None:
        return None

    img = image.convert("RGB")
    W, H = img.size
    pixels = list(img.getdata())
    total = W * H
    out_pixels = []

    for y in range(H):
        row_start = (H - 1 - y) * W
        out_pixels.extend(pixels[row_start + W - 1 - x] for x in range(W))
        if on_progress:
            on_progress((y + 1) * W, total)

    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    return out


def flip_horizontal(image, on_progress=None):
    """
    Espelhamento horizontal (esquerda ↔ direita) — sem numpy/opencv.

    Mapeamento: dst(out_x, out_y) = src(W-1-out_x, out_y)
    Equivalente a inverter cada linha individualmente.
    """
    if image is None:
        return None

    img = image.convert("RGB")
    W, H = img.size
    pixels = list(img.getdata())
    total = W * H
    out_pixels = []

    for y in range(H):
        row = pixels[y * W:(y + 1) * W]
        out_pixels.extend(row[::-1])
        if on_progress:
            on_progress((y + 1) * W, total)

    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    return out


def flip_vertical(image, on_progress=None):
    """
    Espelhamento vertical (cima ↔ baixo) — sem numpy/opencv.

    Mapeamento: dst(out_x, out_y) = src(out_x, H-1-out_y)
    Equivalente a inverter a ordem das linhas.
    """
    if image is None:
        return None

    img = image.convert("RGB")
    W, H = img.size
    pixels = list(img.getdata())
    total = W * H
    out_pixels = []

    for y in range(H):
        src_row_start = (H - 1 - y) * W
        out_pixels.extend(pixels[src_row_start:src_row_start + W])
        if on_progress:
            on_progress((y + 1) * W, total)

    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    return out


def ascii_art_filter(image, block_size=8, on_progress=None):
    """
    Filtro Arte ASCII — sem numpy/opencv.

    Divide a imagem em blocos de block_size×block_size pixels.
    Para cada bloco calcula o brilho médio e mapeia a um caractere da
    rampa ASCII: área clara → espaço, área escura → char denso (padrão
    clássico — fundo branco, texto escuro).

    block_size: tamanho do bloco em pixels (4–32).
    """
    if image is None:
        return None

    from PIL import ImageDraw, ImageFont

    # Rampa do MAIS DENSO ao MAIS ESPARSO — fonte escura sobre fundo branco.
    # Pixel escuro (0) → índice 0 (@), pixel claro (255) → índice -1 (espaço).
    ASCII_RAMP = "@%#&BWM8RD$0GAONHQK5b69hkdpqwmXYZEFPST43C72aefgjnorsuvxyz1ltic!?><;:^~-_,.'` "

    img = image.convert("L")
    W, H = img.size
    pixels = img.load()

    bs = max(2, block_size)
    cols = max(1, W // bs)
    rows = max(1, H // bs)
    total_px = W * H          # mesmo denominador que os outros filtros usam
    ramp_len = len(ASCII_RAMP)

    # Tenta carregar fonte monoespaçada do tamanho do bloco
    font = None
    for path in [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]:
        try:
            font = ImageFont.truetype(path, bs)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    # Mede a célula real do caractere para evitar sobreposição
    try:
        bbox = font.getbbox("@")
        cell_w = max(1, bbox[2] - bbox[0])
        cell_h = max(1, bbox[3] - bbox[1])
    except Exception:
        cell_w = cell_h = bs

    # Dimensão de saída: cada bloco de amostra gera uma célula de texto
    out_w = cols * cell_w
    out_h = rows * cell_h
    out = Image.new("RGB", (out_w, out_h), (255, 255, 255))   # fundo branco
    draw = ImageDraw.Draw(out)

    done_px = 0
    for row in range(rows):
        y0 = row * bs
        y1 = min(y0 + bs, H)
        for col in range(cols):
            x0 = col * bs
            x1 = min(x0 + bs, W)

            # Brilho médio do bloco (loop puro, sem numpy)
            total_lum = 0
            count = 0
            for py in range(y0, y1):
                for px in range(x0, x1):
                    total_lum += pixels[px, py]
                    count += 1
            avg = total_lum // count if count else 0

            # Escuro (0) → char denso; claro (255) → espaço
            char = ASCII_RAMP[int((255 - avg) / 255 * (ramp_len - 1))]

            # Renderiza com tom de cinza correspondente ao original
            gray = avg // 3          # chars nunca ficam totalmente brancos
            draw.text((col * cell_w, row * cell_h), char,
                      fill=(gray, gray, gray), font=font)

            done_px += bs * bs
            if on_progress:
                on_progress(min(done_px, total_px), total_px)

    # Redimensiona para as dimensões originais mantendo os chars visíveis
    if (out_w, out_h) != (W, H):
        out = out.resize((W, H), Image.NEAREST)

    return out


# ---------------------------------------------------------------------------
# Efeitos Especiais
# ---------------------------------------------------------------------------

def heatmap_filter(image, on_progress=None):
    """
    Mapa Térmico — sem numpy/opencv.

    Converte para escala de cinza e mapeia cada nível de luminosidade
    a uma cor do gradiente térmico clássico:
        0 (escuro) → azul → ciano → verde → amarelo → vermelho → 255 (claro)

    Usa LUT (lookup table) de 256 entradas para evitar recalcular
    a interpolação para cada pixel.
    """
    if image is None:
        return None

    # Pontos de controle: (luminosidade, (R, G, B))
    STOPS = [
        (0,   (0,   0,   255)),   # azul
        (64,  (0,   255, 255)),   # ciano
        (128, (0,   255, 0  )),   # verde
        (192, (255, 255, 0  )),   # amarelo
        (255, (255, 0,   0  )),   # vermelho
    ]

    # Pré-computa LUT para todos os 256 valores possíveis
    lut = [None] * 256
    for v in range(256):
        for i in range(len(STOPS) - 1):
            v0, c0 = STOPS[i]
            v1, c1 = STOPS[i + 1]
            if v0 <= v <= v1:
                t = (v - v0) / (v1 - v0)
                lut[v] = tuple(int(c0[j] + t * (c1[j] - c0[j])) for j in range(3))
                break

    img = image.convert("L")
    W, H = img.size
    pixels = list(img.getdata())
    total = W * H
    out_pixels = []

    for i, v in enumerate(pixels):
        out_pixels.append(lut[v])
        if on_progress and i % (W * 8) == 0:
            on_progress(i, total)

    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    if on_progress:
        on_progress(total, total)
    return out


def glitch_filter(image, intensity=8, on_progress=None):
    """
    Efeito Glitch — sem numpy/opencv.

    Combina quatro camadas de corrupção de sinal digital:
      1. Aberração cromática por linha (R e B deslocados opostamente)
      2. Block tears — blocos horizontais inteiros deslocados drasticamente
      3. Scanlines corrompidas — linhas com cores invertidas
      4. Offset global do canal R (desalinhamento de sinal persistente)

    intensity (1–30): controla intensidade de todos os efeitos.
    """
    if image is None:
        return None

    import random
    rng = random.Random(intensity * 31337)   # seed determinístico por intensidade

    img = image.convert("RGB")
    W, H = img.size
    raw = list(img.getdata())
    total = W * H

    r_ch = [p[0] for p in raw]
    g_ch = [p[1] for p in raw]
    b_ch = [p[2] for p in raw]

    prob      = intensity / 30.0
    max_shift = max(2, int(W * prob * 0.5))

    # --- 1. Aberração cromática linha a linha ---
    for y in range(H):
        if rng.random() < prob * 0.8:
            rs = y * W
            sr = rng.randint(2, max_shift) % W
            sb = rng.randint(2, max_shift) % W

            row = r_ch[rs:rs + W]
            r_ch[rs:rs + W] = row[W - sr:] + row[:W - sr]

            row = b_ch[rs:rs + W]
            b_ch[rs:rs + W] = row[sb:] + row[:sb]

        if on_progress and y % 30 == 0:
            on_progress(int((y / H) * total * 0.4), total)

    # --- 2. Block tears — blocos deslocados com shift grande ---
    n_tears = max(2, int(intensity * 0.7))
    for _ in range(n_tears):
        y0     = rng.randint(0, H - 1)
        bh     = rng.randint(3, max(4, H // 6))
        shift  = rng.randint(W // 5, W // 2) * rng.choice([-1, 1])
        s      = shift % W
        for y in range(y0, min(y0 + bh, H)):
            rs = y * W
            for ch in (r_ch, g_ch, b_ch):
                row = ch[rs:rs + W]
                ch[rs:rs + W] = row[W - s:] + row[:W - s]

    if on_progress:
        on_progress(int(total * 0.6), total)

    # --- 3. Scanlines corrompidas — inverte cor de linhas aleatórias ---
    n_corrupt = max(1, intensity // 4)
    for _ in range(n_corrupt):
        y  = rng.randint(0, H - 1)
        rs = y * W
        for x in range(W):
            i = rs + x
            r_ch[i] = 255 - r_ch[i]
            g_ch[i] = 255 - g_ch[i]
            b_ch[i] = 255 - b_ch[i]

    if on_progress:
        on_progress(int(total * 0.8), total)

    # --- 4. Offset global do canal R (desalinhamento de sinal persistente) ---
    global_s = max(1, int(W * prob * 0.06)) % W
    for y in range(H):
        rs = y * W
        row = r_ch[rs:rs + W]
        r_ch[rs:rs + W] = row[W - global_s:] + row[:W - global_s]

    out_pixels = list(zip(r_ch, g_ch, b_ch))
    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    if on_progress:
        on_progress(total, total)
    return out


def dither_floyd_steinberg(image, levels=2, on_progress=None):
    """
    Dithering Floyd-Steinberg — sem numpy/opencv.

    Quantiza cada canal RGB para `levels` níveis uniformes, distribuindo
    o erro de quantização de cada pixel para seus vizinhos segundo a
    máscara clássica de Floyd-Steinberg:

              [*]  7/16
        3/16  5/16  1/16

    levels (2–16): 2 = preto/branco, valores maiores preservam mais tons.
    """
    if image is None:
        return None

    levels = max(2, levels)
    img = image.convert("RGB")
    W, H = img.size
    raw = list(img.getdata())
    total = W * H

    # Buffer mutável de floats para acumular o erro difundido
    buf = [[list(map(float, raw[y * W + x])) for x in range(W)] for y in range(H)]

    step = 255.0 / (levels - 1)

    def quantize(v):
        return round(v / step) * step

    out_pixels = []

    for y in range(H):
        for x in range(W):
            old = buf[y][x]
            new = [max(0.0, min(255.0, quantize(c))) for c in old]
            buf[y][x] = new
            out_pixels.append(tuple(int(c) for c in new))

            err = [old[c] - new[c] for c in range(3)]

            # Distribui erro — Floyd-Steinberg
            if x + 1 < W:
                buf[y][x + 1] = [buf[y][x + 1][c] + err[c] * 7 / 16 for c in range(3)]
            if y + 1 < H:
                if x - 1 >= 0:
                    buf[y + 1][x - 1] = [buf[y + 1][x - 1][c] + err[c] * 3 / 16 for c in range(3)]
                buf[y + 1][x] = [buf[y + 1][x][c] + err[c] * 5 / 16 for c in range(3)]
                if x + 1 < W:
                    buf[y + 1][x + 1] = [buf[y + 1][x + 1][c] + err[c] * 1 / 16 for c in range(3)]

        if on_progress:
            on_progress((y + 1) * W, total)

    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    return out


def chromatic_aberration(image, strength=5, on_progress=None):
    """
    Aberração Cromática — sem numpy/opencv.

    Simula o defeito óptico real de lentes: cada comprimento de onda
    (canal de cor) é refratado num ângulo ligeiramente diferente,
    causando franja de cor nas bordas — especialmente nos cantos.

    Implementação via escala radial diferente por canal, centrada na
    imagem. Para cada pixel de saída (x, y):

        R → amostra de  centro + offset / (1 + k)   [canal "maior"]
        G → sem deslocamento                          [referência]
        B → amostra de  centro + offset × (1 + k)   [canal "menor"]

    Quanto mais longe do centro, maior a separação entre os canais.
    Usa interpolação bilinear para bordas suaves.

    strength (1–20): mapeia para k = strength / 200  (0.005 a 0.10).
    """
    if image is None:
        return None

    def _bilinear_ch(ch_pixels, W, H, sx, sy):
        """Interpolação bilinear de um único canal (lista plana de int)."""
        if sx < 0 or sx > W - 1 or sy < 0 or sy > H - 1:
            return 0
        x0, y0 = int(sx), int(sy)
        x1 = min(x0 + 1, W - 1)
        y1 = min(y0 + 1, H - 1)
        fx, fy = sx - x0, sy - y0
        return int(
            ch_pixels[y0 * W + x0] * (1 - fx) * (1 - fy) +
            ch_pixels[y0 * W + x1] * fx       * (1 - fy) +
            ch_pixels[y1 * W + x0] * (1 - fx) * fy       +
            ch_pixels[y1 * W + x1] * fx       * fy
        )

    img = image.convert("RGB")
    W, H = img.size
    raw = list(img.getdata())
    total = W * H

    r_ch = [p[0] for p in raw]
    g_ch = [p[1] for p in raw]
    b_ch = [p[2] for p in raw]

    k  = strength / 200.0   # 0.005 … 0.10
    cx = W / 2.0
    cy = H / 2.0

    out_pixels = []
    for y in range(H):
        for x in range(W):
            dx = x - cx
            dy = y - cy

            # R: escala menor na origem → aparece maior na saída (vaza pra fora)
            r_inv = 1.0 / (1.0 + k)
            rx = cx + dx * r_inv
            ry = cy + dy * r_inv
            r  = _bilinear_ch(r_ch, W, H, rx, ry)

            # G: sem deslocamento — canal de referência
            g = g_ch[y * W + x]

            # B: escala maior na origem → aparece menor na saída (encolhe pra dentro)
            bx = cx + dx * (1.0 + k)
            by = cy + dy * (1.0 + k)
            b  = _bilinear_ch(b_ch, W, H, bx, by)

            out_pixels.append((r, g, b))

        if on_progress:
            on_progress((y + 1) * W, total)

    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    return out


def barrel_distortion(image, strength=15, on_progress=None):
    """
    Distorção Barril / Fisheye — sem numpy/opencv.

    Para cada pixel de saída (ox, oy), calcula a posição de origem
    na imagem original usando mapeamento radial:

        r² = ((ox − cx)/norm)² + ((oy − cy)/norm)²
        src = dst_offset × (1 + k × r²)

    k > 0  →  barril/fisheye (centro inflado, bordas comprimidas).
    Usa interpolação bilinear para resultado suave.

    strength (1–50): mapeia para k = strength / 100  (0.01 a 0.50).
    """
    if image is None:
        return None

    import math

    def _bilinear(pixels, W, H, sx, sy):
        """Interpolação bilinear com borda preta."""
        if sx < 0 or sx > W - 1 or sy < 0 or sy > H - 1:
            return (0, 0, 0)
        x0, y0 = int(sx), int(sy)
        x1 = min(x0 + 1, W - 1)
        y1 = min(y0 + 1, H - 1)
        fx, fy = sx - x0, sy - y0
        p00 = pixels[y0 * W + x0]
        p10 = pixels[y0 * W + x1]
        p01 = pixels[y1 * W + x0]
        p11 = pixels[y1 * W + x1]
        return tuple(
            int(p00[c] * (1 - fx) * (1 - fy) + p10[c] * fx * (1 - fy) +
                p01[c] * (1 - fx) * fy       + p11[c] * fx * fy)
            for c in range(3)
        )

    img = image.convert("RGB")
    W, H = img.size
    pixels = list(img.getdata())
    total = W * H

    k    = strength / 100.0
    cx   = W / 2.0
    cy   = H / 2.0
    norm = min(cx, cy)

    out_pixels = []
    for y in range(H):
        for x in range(W):
            nx = (x - cx) / norm
            ny = (y - cy) / norm
            r2 = nx * nx + ny * ny

            factor = 1.0 + k * r2
            sx = nx * factor * norm + cx
            sy = ny * factor * norm + cy

            out_pixels.append(_bilinear(pixels, W, H, sx, sy))

        if on_progress:
            on_progress((y + 1) * W, total)

    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    return out


def ripple_filter(image, amplitude=10, on_progress=None):
    """
    Ondulação (Ripple / Wave) — sem numpy/opencv.

    Desloca cada pixel por um offset sinusoidal dependente da posição,
    criando o efeito de imagem vista através de vidro ondulado ou água:

        src_x = x + A × sin(2π × y / λy)
        src_y = y + A × sin(2π × x / λx)

    Os comprimentos de onda λx e λy são proporcionais às dimensões
    da imagem para que o efeito escale corretamente.

    amplitude (1–40): altura máxima da onda em pixels.
    """
    if image is None:
        return None

    import math

    img = image.convert("RGB")
    W, H = img.size
    pixels = list(img.getdata())
    total = W * H

    lambda_x = W / 5.0
    lambda_y = H / 5.0
    out_pixels = []

    for y in range(H):
        for x in range(W):
            dx = amplitude * math.sin(2 * math.pi * y / lambda_y)
            dy = amplitude * math.sin(2 * math.pi * x / lambda_x)

            sx = max(0, min(W - 1, int(x + dx + 0.5)))
            sy = max(0, min(H - 1, int(y + dy + 0.5)))
            out_pixels.append(pixels[sy * W + sx])

        if on_progress:
            on_progress((y + 1) * W, total)

    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    return out


def frosted_glass_filter(image, radius=5, on_progress=None):
    """
    Vidro Fosco (Frosted Glass) — sem numpy/opencv.

    Para cada pixel de saída, amostra um pixel da entrada em uma
    posição aleatória dentro de um raio r, simulando a dispersão
    da luz ao passar por vidro texturizado/fosco.

    Usa um gerador com seed fixo para resultado reproduzível.

    radius (1–20): raio máximo de dispersão em pixels.
    """
    if image is None:
        return None

    import random
    rng = random.Random(7919)   # seed fixo — mesmo resultado toda vez

    img = image.convert("RGB")
    W, H = img.size
    pixels = list(img.getdata())
    total = W * H
    out_pixels = []

    for y in range(H):
        for x in range(W):
            dx = rng.randint(-radius, radius)
            dy = rng.randint(-radius, radius)
            sx = max(0, min(W - 1, x + dx))
            sy = max(0, min(H - 1, y + dy))
            out_pixels.append(pixels[sy * W + sx])

        if on_progress:
            on_progress((y + 1) * W, total)

    out = Image.new("RGB", (W, H))
    out.putdata(out_pixels)
    return out


def downscale(image, factor=4, on_progress=None):
    """
    Degradação de qualidade — pipeline inverso ao upscale.

    Etapas (ao contrário do upscale):
    1. Blur Gaussiano — perde nitidez (inverso do sharpening)
    2. Reduz a resolução real com INTER_AREA — perde informação de pixel
    3. Reampliar com NEAREST — pixelação clássica / despixelização reversa
    4. Ruído Gaussiano — desfaz o denoising, introduz granulação

    factor: intensidade da degradação (4 = bloco 4×4 visível + ruído proporcional)
    """
    if image is None:
        return None

    import cv2
    import numpy as np

    factor = max(2, factor)
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    h, w = bgr.shape[:2]

    # 1. Blur Gaussiano (perde nitidez — inverso do unsharp mask)
    blurred = cv2.GaussianBlur(bgr, (0, 0), sigmaX=float(factor))

    # 2. Reduz resolução real (perde informação)
    small_w, small_h = max(1, w // factor), max(1, h // factor)
    small = cv2.resize(blurred, (small_w, small_h), interpolation=cv2.INTER_AREA)

    # 3. Reampliar com NEAREST (pixelação visível)
    pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    # 4. Ruído Gaussiano (inverso do denoising)
    noise = np.random.normal(0, factor * 3.0, pixelated.shape).astype(np.float32)
    noisy = np.clip(pixelated.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    result_rgb = cv2.cvtColor(noisy, cv2.COLOR_BGR2RGB)
    print(f"Downscale: {w}×{h} → {small_w}×{small_h} → {w}×{h} (blur + pixelação + ruído, ×{factor})")
    return Image.fromarray(result_rgb)


def upscale(image, factor=2, on_progress=None):
    """
    Super-resolução / aprimoramento de qualidade.

    Etapas:
    1. LANCZOS4 — melhor interpolação do OpenCV para upscaling
    2. Non-Local Means denoising — remove ruído/granulação preservando bordas
    3. Unsharp mask agressivo — desborrar e aumentar nitidez
    4. CLAHE no canal L (LAB) — melhora contraste local sem saturar

    factor: multiplicador de tamanho (2 = dobro, 3 = triplo, etc.)
    """
    if image is None:
        return None

    import cv2
    import numpy as np

    factor = max(2, factor)
    img_rgb = image.convert("RGB")
    arr = np.array(img_rgb)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    h, w = bgr.shape[:2]

    # 1. Upscale com melhor interpolação
    upscaled = cv2.resize(bgr, (w * factor, h * factor), interpolation=cv2.INTER_LANCZOS4)

    # 2. Denoising com Non-Local Means (preserva bordas melhor que filtro Gaussiano)
    denoised = cv2.fastNlMeansDenoisingColored(
        upscaled, None, h=10, hColor=10,
        templateWindowSize=7, searchWindowSize=21,
    )

    # 3. Unsharp mask agressivo para desborrar / aumentar nitidez
    blurred = cv2.GaussianBlur(denoised, (0, 0), sigmaX=2.0)
    sharpened = cv2.addWeighted(denoised, 2.0, blurred, -1.0, 0)

    # 4. CLAHE no canal L (espaço LAB) — melhora contraste local sem mexer em cor
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab_enhanced = cv2.merge([clahe.apply(l), a, b])
    result = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    print(f"Upscale: {w}×{h} → {w*factor}×{h*factor} (LANCZOS4 + NLM + unsharp mask + CLAHE, ×{factor})")
    return Image.fromarray(result_rgb)
