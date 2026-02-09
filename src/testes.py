import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QVBoxLayout, QFileDialog
)
from PySide6.QtGui import QPixmap
from PIL import Image
from PIL.ImageQt import ImageQt


class Janela(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Carregar imagem (PySide6)")

        self.botao = QPushButton("Escolher imagem")
        self.botao.clicked.connect(self.carregar_imagem)

        self.label = QLabel("Nenhuma imagem carregada")
        self.label.setScaledContents(True)  # imagem se adapta ao label

        layout = QVBoxLayout()
        layout.addWidget(self.botao)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def carregar_imagem(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Escolha uma imagem",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if caminho:
            # Abre com PIL
            img = Image.open(caminho)

            # Converte PIL -> Qt
            img_qt = ImageQt(img)

            # QPixmap para exibir no QLabel
            pixmap = QPixmap.fromImage(img_qt)

            self.label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = Janela()
    janela.resize(400, 400)
    janela.show()
    sys.exit(app.exec())
