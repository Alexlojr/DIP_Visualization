from PIL import Image

img = Image.open("test-image.jpg").convert("RGB")

for y in range(img.height):
    for x in range(img.width):
        r,g,b = img.getpixel((x, y))

        L = int(0.299*r + 0.587*g + 0.114*b)

        if L >128:
            L = 128
        else:
            L = 0

        img.putpixel((x, y), L)

        img.putpixel((x, y), (r, g, b))