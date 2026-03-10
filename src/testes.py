import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

MAX_EXIBICAO = 400  # tamanho máximo para exibição na tela

img_original = None


def redimensionar_para_exibicao(img):
    """Redimensiona mantendo proporção para caber em MAX_EXIBICAO x MAX_EXIBICAO"""
    img_copia = img.copy()
    img_copia.thumbnail((MAX_EXIBICAO, MAX_EXIBICAO))
    return img_copia


def carregar_imagem():
    global img_original

    caminho = filedialog.askopenfilename(
        filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")]
    )
    if not caminho:
        return

    img_original = Image.open(caminho).convert("RGB")

    exibicao = redimensionar_para_exibicao(img_original)
    foto = ImageTk.PhotoImage(exibicao)
    label_original.config(image=foto, width=exibicao.width, height=exibicao.height)
    label_original.image = foto

    label_filtrada.config(image="", width=exibicao.width, height=exibicao.height)
    label_filtrada.image = None

    ajustar_janela()


def aplicar_filtro():
    if img_original is None:
        return

    limiar = int(entry_limiar.get())

    img = img_original.copy()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = img.getpixel((x, y))

            L = int(0.299*r + 0.587*g + 0.114*b)

            if L > limiar:
                L = 255
            else:
                L = 0

            img.putpixel((x, y), (L, L, L))

    # Redimensiona só para exibição
    exibicao = redimensionar_para_exibicao(img)
    foto = ImageTk.PhotoImage(exibicao)
    label_filtrada.config(image=foto, width=exibicao.width, height=exibicao.height)
    label_filtrada.image = foto

    ajustar_janela()


def ajustar_janela():
    root.update_idletasks()
    root.geometry("")


# --- janela ---
root = tk.Tk()
root.title("Teste de Filtro")

frame_controles = tk.Frame(root)
frame_controles.pack(pady=10, padx=10, anchor="w")

btn_carregar = tk.Button(frame_controles, text="Carregar Imagem", command=carregar_imagem, padx=8, pady=4)
btn_carregar.grid(row=0, column=0, padx=(0, 20))

tk.Label(frame_controles, text="Limiar (0-255):").grid(row=0, column=1)
entry_limiar = tk.Entry(frame_controles, width=6)
entry_limiar.insert(0, "128")
entry_limiar.grid(row=0, column=2, padx=5)

btn_aplicar = tk.Button(frame_controles, text="Aplicar Binarização", command=aplicar_filtro, padx=8, pady=4)
btn_aplicar.grid(row=0, column=3, padx=(10, 0))

frame_imagens = tk.Frame(root)
frame_imagens.pack(padx=10, pady=(0, 10))

tk.Label(frame_imagens, text="Original").grid(row=0, column=0, pady=(0, 4))
tk.Label(frame_imagens, text="Binarizada").grid(row=0, column=1, pady=(0, 4))

label_original = tk.Label(frame_imagens, bg="#e0e0e0", width=40, height=20)
label_original.grid(row=1, column=0, padx=(0, 10))

label_filtrada = tk.Label(frame_imagens, bg="#e0e0e0", width=40, height=20)
label_filtrada.grid(row=1, column=1)

root.mainloop()