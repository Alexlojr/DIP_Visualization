from PIL import Image

def mean_filter(image, kernel_size=3):
    """
    Manual Mean Filter without NumPy or OpenCV
    """
    if image is None: return None
    if kernel_size % 2 == 0:
        raise ValueError("Kernel size must be odd")

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))

    pixels = img.load()
    new_pixels = new_img.load()

    indexer = kernel_size // 2

    for x in range(width):
        for y in range(height):
            r_sum, g_sum, b_sum = 0, 0, 0
            count = 0

            for i in range(x - indexer, x + indexer + 1):
                for j in range(y - indexer, y + indexer + 1):
                    # Check bounds explicitly
                    if (0 <= i < width) and (0 <= j < height):
                        r, g, b = pixels[i, j]
                        r_sum += r
                        g_sum += g
                        b_sum += b
                        count += 1

            new_pixels[x, y] = (r_sum // count, g_sum // count, b_sum // count)

    print(f"Applying Mean Filter with kernel size {kernel_size}")
    return new_img

def median_filter(image, kernel_size=3):
    """
    Manual Median Filter without NumPy or OpenCV
    """
    if image is None: return None
    if kernel_size % 2 == 0:
        raise ValueError("Kernel size must be odd")

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))

    pixels = img.load()
    new_pixels = new_img.load()

    indexer = kernel_size // 2

    for x in range(width):
        for y in range(height):
            r_vals, g_vals, b_vals = [], [], []

            for i in range(x - indexer, x + indexer + 1):
                for j in range(y - indexer, y + indexer + 1):
                    if (0 <= i < width) and (0 <= j < height):
                        r, g, b = pixels[i, j]
                        r_vals.append(r)
                        g_vals.append(g)
                        b_vals.append(b)

            r_vals.sort()
            g_vals.sort()
            b_vals.sort()

            mid = len(r_vals) // 2
            new_pixels[x, y] = (r_vals[mid], g_vals[mid], b_vals[mid])

    print(f"Applying Median Filter with kernel size {kernel_size}")
    return new_img

def sobel_filter(image):
    """
    Placeholder for Sobel Filter.
    """
    print("Applying Sobel Filter")
    return image.copy() if image else None

def laplacian_filter(image):
    """
    Placeholder for Laplacian Filter.
    """
    print("Applying Laplacian Filter")
    return image.copy() if image else None
