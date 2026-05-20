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
                    # kernel row i -> y offset (i - 1), col j -> x offset (j - 1)
                    px = pixels[x + j - 1, y + i - 1]
                    gx += Gx[i][j] * px; gy += Gy[i][j] * px
            new_pixels[x, y] = min(255, int(math.sqrt(gx * gx + gy * gy)))
        if on_progress:
            on_progress((x) * (height - 2), total)

    return new_img


def laplacian_filter(image, on_progress=None):
    """Laplacian edge response: |∇²I|, scaled to 0-255 for visibility; output RGB."""
    if image is None: return None

    img = image.convert("L")
    width, height = img.size
    pixels = img.load()
    kernel = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    total = width * height

    # Collect |response|; raw values are often small on natural images and look black if not scaled
    magnitudes: list[int] = []
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            val = 0
            for i in range(3):
                for j in range(3):
                    val += kernel[i][j] * pixels[x + j - 1, y + i - 1]
            magnitudes.append(abs(val))
        if on_progress:
            on_progress((x + 1) * height, total)

    mx = max(magnitudes) if magnitudes else 0

    new_img = Image.new("RGB", (width, height))
    new_pixels = new_img.load()
    k = 0
    if mx == 0:
        # Uniform or perfectly linear regions give ~0 Laplacian; avoid an all-black preview
        fill = (128, 128, 128)
        for x in range(1, width - 1):
            for y in range(1, height - 1):
                new_pixels[x, y] = fill
    else:
        for x in range(1, width - 1):
            for y in range(1, height - 1):
                v = min(255, magnitudes[k] * 255 // mx)
                new_pixels[x, y] = (v, v, v)
                k += 1

    if on_progress:
        on_progress(total, total)

    for x in range(width):
        new_pixels[x, 0] = (0, 0, 0)
        new_pixels[x, height - 1] = (0, 0, 0)
    for y in range(height):
        new_pixels[0, y] = (0, 0, 0)
        new_pixels[width - 1, y] = (0, 0, 0)

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
                    px = pixels[x + j - 1, y + i - 1]
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
                    r, g, b = pixels[x + j - 1, y + i - 1]
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


def mode_filter(image, kernel_size=3, on_progress=None):
    """
    Filtro de Moda — substitui cada pixel pelo valor mais frequente
    (moda estatística) na vizinhança kernel_size × kernel_size.

    Diferente do mediana (valor central da lista ordenada), a moda
    pega o valor que aparece mais vezes. Tende a criar regiões de cor
    uniforme e preservar bordas abruptas, com efeito de posterização
    suave.

    O cálculo é feito canal a canal (R, G, B independentemente).
    """
    if image is None: return None
    if kernel_size % 2 == 0:
        kernel_size += 1

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    half = kernel_size // 2
    total = width * height

    for x in range(width):
        for y in range(height):
            r_freq = {}
            g_freq = {}
            b_freq = {}
            for i in range(x - half, x + half + 1):
                for j in range(y - half, y + half + 1):
                    if 0 <= i < width and 0 <= j < height:
                        r, g, b = pixels[i, j]
                        r_freq[r] = r_freq.get(r, 0) + 1
                        g_freq[g] = g_freq.get(g, 0) + 1
                        b_freq[b] = b_freq.get(b, 0) + 1
            new_pixels[x, y] = (
                max(r_freq, key=r_freq.get),
                max(g_freq, key=g_freq.get),
                max(b_freq, key=b_freq.get),
            )
        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


def kuwahara_filter(image, kernel_size=5, on_progress=None):
    """
    Filtro Kuwahara — suaviza preservando bordas.

    Para cada pixel, divide a vizinhança em 4 sub-regiões quadradas
    sobrepostas (cada uma inclui o pixel central):

        ┌───┬───┐
        │ Q1│ Q2│
        ├───┼───┤
        │ Q3│ Q4│
        └───┴───┘

    Calcula a média e variância de cada quadrante e atribui ao pixel
    a média do quadrante com menor variância (região mais homogênea).

    Resultado: suavização dentro de regiões uniformes, bordas nítidas.
    Efeito visual similar a pintura a óleo.

    kernel_size (ímpar ≥ 3): tamanho total da janela. Cada quadrante
    tem tamanho ((kernel_size + 1) / 2) × ((kernel_size + 1) / 2).
    """
    if image is None: return None
    if kernel_size % 2 == 0:
        kernel_size += 1

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    half = kernel_size // 2
    total = width * height

    for x in range(width):
        for y in range(height):
            # 4 quadrantes: (x_start, y_start) de cada um
            quadrants = [
                (x - half, y - half),   # Q1 — superior esquerdo
                (x,        y - half),   # Q2 — superior direito
                (x - half, y       ),   # Q3 — inferior esquerdo
                (x,        y       ),   # Q4 — inferior direito
            ]
            q_size = half + 1   # lado de cada quadrante

            best_var  = None
            best_mean = (0, 0, 0)

            for qx, qy in quadrants:
                r_vals, g_vals, b_vals = [], [], []
                for i in range(qx, qx + q_size):
                    for j in range(qy, qy + q_size):
                        ii = max(0, min(width  - 1, i))
                        jj = max(0, min(height - 1, j))
                        r, g, b = pixels[ii, jj]
                        r_vals.append(r)
                        g_vals.append(g)
                        b_vals.append(b)

                n = len(r_vals)
                mr = sum(r_vals) / n
                mg = sum(g_vals) / n
                mb = sum(b_vals) / n

                # Variância combinada dos 3 canais
                var = (
                    sum((v - mr) ** 2 for v in r_vals) +
                    sum((v - mg) ** 2 for v in g_vals) +
                    sum((v - mb) ** 2 for v in b_vals)
                ) / n

                if best_var is None or var < best_var:
                    best_var  = var
                    best_mean = (int(mr), int(mg), int(mb))

            new_pixels[x, y] = best_mean

        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


# ---------------------------------------------------------------------------
# Filtro Bilateral (Passa Baixa — preserva bordas)
# ---------------------------------------------------------------------------

def bilateral_filter(image, kernel_size=5, sigma_space=None, sigma_intensity=30, on_progress=None):
    """
    Filtro Bilateral — suavização que preserva bordas.

    Diferente dos filtros lineares (média, gaussiano), o bilateral pondera
    cada vizinho por DOIS fatores:
      1. Proximidade espacial (como o gaussiano)
      2. Similaridade de intensidade (pixels com cor parecida pesam mais)

    Resultado: regiões homogêneas ficam suaves, mas bordas abruptas
    (onde a intensidade muda muito) são preservadas.

    Muito usado em: denoising de fotos, pré-processamento para segmentação,
    e efeito de "pele suave" em retratos.

    kernel_size (ímpar ≥ 3): tamanho da janela.
    sigma_intensity (1–100): tolerância de diferença de cor.
    """
    if image is None:
        return None
    if kernel_size % 2 == 0:
        kernel_size += 1

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    half = kernel_size // 2
    total = width * height

    # sigma_space default: proporcional ao kernel
    if sigma_space is None:
        sigma_space = kernel_size / 3.0

    ss2 = 2.0 * sigma_space * sigma_space
    si2 = 2.0 * sigma_intensity * sigma_intensity

    for x in range(width):
        for y in range(height):
            r0, g0, b0 = pixels[x, y]

            r_sum = g_sum = b_sum = 0.0
            w_sum = 0.0

            for i in range(x - half, x + half + 1):
                for j in range(y - half, y + half + 1):
                    if 0 <= i < width and 0 <= j < height:
                        r, g, b = pixels[i, j]

                        # Peso espacial (distância geométrica)
                        dx = i - x
                        dy = j - y
                        w_space = math.exp(-(dx * dx + dy * dy) / ss2)

                        # Peso de intensidade (diferença de cor)
                        dr = r - r0
                        dg = g - g0
                        db = b - b0
                        diff2 = dr * dr + dg * dg + db * db
                        w_intensity = math.exp(-diff2 / si2)

                        w = w_space * w_intensity
                        r_sum += r * w
                        g_sum += g * w
                        b_sum += b * w
                        w_sum += w

            if w_sum > 0:
                new_pixels[x, y] = (
                    int(r_sum / w_sum),
                    int(g_sum / w_sum),
                    int(b_sum / w_sum),
                )
            else:
                new_pixels[x, y] = (r0, g0, b0)

        if on_progress:
            on_progress((x + 1) * height, total)

    return new_img


# ---------------------------------------------------------------------------
# Roberts Cross (Passa Alta — detecção de bordas 2×2)
# ---------------------------------------------------------------------------

def roberts_cross_filter(image, on_progress=None):
    """
    Filtro Roberts Cross — detecção de bordas com kernel 2×2.

    Um dos operadores de borda mais antigos e simples. Usa dois kernels
    2×2 cruzados em diagonal:

        Gx = [[1,  0],     Gy = [[ 0, 1],
              [0, -1]]           [-1, 0]]

    Magnitude: |G| = sqrt(Gx² + Gy²)

    Vantagem sobre Sobel/Prewitt: resposta mais fina (bordas de 1px),
    detecta melhor bordas diagonais. Desvantagem: mais sensível a ruído.
    """
    if image is None:
        return None

    img = image.convert("L")
    width, height = img.size
    new_img = Image.new("L", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = (width - 1) * (height - 1)

    for x in range(width - 1):
        for y in range(height - 1):
            # Gx = p(x,y) - p(x+1,y+1)
            gx = pixels[x, y] - pixels[x + 1, y + 1]
            # Gy = p(x+1,y) - p(x,y+1)
            gy = pixels[x + 1, y] - pixels[x, y + 1]

            new_pixels[x, y] = min(255, int(math.sqrt(gx * gx + gy * gy)))

        if on_progress:
            on_progress((x + 1) * (height - 1), total)

    return new_img


# ---------------------------------------------------------------------------
# Emboss (Passa Alta — relevo 3D)
# ---------------------------------------------------------------------------

def emboss_filter(image, on_progress=None):
    """
    Filtro Emboss (Relevo) — cria efeito de relevo 3D.

    Usa um kernel direcional que realça a transição de escuro→claro
    na diagonal superior-esquerda → inferior-direita, simulando uma
    fonte de luz vinda do canto superior esquerdo:

        [[-2, -1, 0],
         [-1,  1, 1],
         [ 0,  1, 2]]

    O resultado é somado a 128 (cinza médio) para que regiões planas
    fiquem cinza neutro, bordas "iluminadas" fiquem claras e bordas
    "sombreadas" fiquem escuras.
    """
    if image is None:
        return None

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))
    pixels = img.load()
    new_pixels = new_img.load()
    total = (width - 2) * (height - 2)

    kernel = [[-2, -1, 0],
              [-1,  1, 1],
              [ 0,  1, 2]]

    for x in range(1, width - 1):
        for y in range(1, height - 1):
            r_val = g_val = b_val = 0
            for i in range(3):
                for j in range(3):
                    r, g, b = pixels[x + j - 1, y + i - 1]
                    k = kernel[i][j]
                    r_val += k * r
                    g_val += k * g
                    b_val += k * b
            # Offset de 128 para que áreas planas fiquem cinza neutro
            new_pixels[x, y] = (
                min(255, max(0, r_val + 128)),
                min(255, max(0, g_val + 128)),
                min(255, max(0, b_val + 128)),
            )
        if on_progress:
            on_progress((x) * (height - 2), total)

    # Bordas: copia pixels originais
    for x in range(width):
        new_pixels[x, 0] = pixels[x, 0]
        new_pixels[x, height - 1] = pixels[x, height - 1]
    for y in range(height):
        new_pixels[0, y] = pixels[0, y]
        new_pixels[width - 1, y] = pixels[width - 1, y]

    return new_img

