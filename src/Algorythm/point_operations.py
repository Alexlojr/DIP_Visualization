from PIL import Image

def binarization(image, threshold=127):
    """
    Manual Binarization without NumPy or OpenCV
    """
    if image is None: return None
    
    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("L", (width, height))
    
    pixels = img.load()
    new_pixels = new_img.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            if gray >= threshold:
                new_pixels[x, y] = 255
            else:
                new_pixels[x, y] = 0
                
    return new_img



def grayscale(image, threshold=127):
    """
    Manual Grayscale conversion without NumPy or OpenCV
    """

    if image is None: return None

    # The image MUST be converted to RGB first to unpack r, g, b
    img = image.convert("RGB")
    width, height = img.size
    
    # We create a new image with mode "L" (Luminance/Grayscale)
    new_img = Image.new("L", (width, height))

    pixels = img.load()
    new_pixels = new_img.load()

    for x in range(width):
        for y in range(height):
            # Since we converted img to RGB, we can safely unpack r, g, b
            r, g, b = pixels[x, y]

            # Calculate the grayscale value
            luminance = int(0.299 * r + 0.587 * g + 0.114 * b)

            # Assign the calculated luminance directly to the pixel
            new_pixels[x, y] = luminance

    print("Applying Grayscale")
    return new_img





def histogram_equalization(image):
    """
    Placeholder for Histogram Equalization.
    """
    print("Applying Histogram Equalization")
    return image.copy() if image else None

def quantization(image, levels=8):
    """
    Placeholder for Quantization.
    """
    print(f"Applying Quantization with {levels} levels")
    return image.copy() if image else None

def invert_colors(image):
    """
    Manual Invert Colors (Negative) filter without NumPy or OpenCV
    """
    if image is None: return None

    img = image.convert("RGB")
    width, height = img.size
    new_img = Image.new("RGB", (width, height))

    pixels = img.load()
    new_pixels = new_img.load()

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            new_pixels[x, y] = (255 - r, 255 - g, 255 - b)

    print("Applying Invert Colors")
    return new_img
