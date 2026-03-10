import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSlider, QScrollArea, QRadioButton,
    QGroupBox, QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont, QColor, QPalette
from PIL import Image
from PIL.ImageQt import ImageQt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDI Visualization - Processamento Digital de Imagens")
        self.setMinimumSize(1200, 800)

        self.setupUi()

    def setupUi(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # --- LEFT PANEL: Controls & Info ---
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        file_group = QGroupBox("Arquivo")
        file_layout = QVBoxLayout(file_group)
        self.load_btn = QPushButton("Carregar Imagem")
        self.load_btn.setObjectName("primaryBtn")
        self.load_btn.clicked.connect(self.load_image)  # <-- conectado aqui
        self.save_btn = QPushButton("Salvar Resultado")
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.save_btn)
        left_panel.addWidget(file_group)

        info_group = QGroupBox("Informações")
        info_layout = QVBoxLayout(info_group)
        info_layout.addWidget(QLabel("Resolução: Placeholder"))
        info_layout.addWidget(QLabel("Canais: RGB"))
        info_layout.addWidget(QLabel("Formato: .png"))
        left_panel.addWidget(info_group)

        left_panel.addStretch()
        main_layout.addLayout(left_panel, 1)

        # --- CENTER PANEL: Images & Histograms ---
        center_panel = QVBoxLayout()
        center_panel.setSpacing(10)

        # Top Area: Images
        images_layout = QHBoxLayout()

        # Original Image Container
        orig_container = QVBoxLayout()
        orig_container.addWidget(QLabel("Imagem Original", alignment=Qt.AlignCenter))
        self.orig_preview = QFrame()
        self.orig_preview.setObjectName("imagePlaceholder")
        self.orig_preview.setMinimumSize(400, 400)
        orig_container.setContentsMargins(0, 0, 0, 80)
        self.orig_preview_label = QLabel("Original", self.orig_preview)
        self.orig_preview_label.setAlignment(Qt.AlignCenter)

        orig_container.addWidget(self.orig_preview)
        images_layout.addLayout(orig_container)

        # Processed Image Container
        proc_container = QVBoxLayout()
        proc_container.addWidget(QLabel("Imagem Alterada", alignment=Qt.AlignCenter))
        self.proc_preview = QFrame()
        self.proc_preview.setObjectName("imagePlaceholder")
        self.proc_preview.setMinimumSize(400, 400)
        proc_container.setContentsMargins(0, 0, 0, 80)
        self.proc_preview_label = QLabel("Alterada", self.proc_preview)
        self.proc_preview_label.setAlignment(Qt.AlignCenter)
        proc_container.addWidget(self.proc_preview)
        images_layout.addLayout(proc_container)

        center_panel.addLayout(images_layout)

        # Slider Middle
        # self.param_slider = QSlider(Qt.Vertical)
        # self.param_slider.setRange(0, 255)
        # self.param_slider.setValue(127)
        # images_layout.addWidget(self.param_slider)

        # Bottom Area: Histograms
        hist_layout = QHBoxLayout()

        self.orig_hist = QFrame()
        self.orig_hist.setObjectName("graphPlaceholder")
        self.orig_hist.setMinimumHeight(200)
        self.orig_hist_label = QLabel("Histograma Original", self.orig_hist)
        self.orig_hist_label.setAlignment(Qt.AlignCenter)
        hist_layout.addWidget(self.orig_hist)

        self.proc_hist = QFrame()
        self.proc_hist.setObjectName("graphPlaceholder")
        self.proc_hist.setMinimumHeight(200)
        self.proc_hist_label = QLabel("Histograma Alterado", self.proc_hist)
        self.proc_hist_label.setAlignment(Qt.AlignCenter)
        hist_layout.addWidget(self.proc_hist)

        center_panel.addLayout(hist_layout)

        main_layout.addLayout(center_panel, 4)

        # --- RIGHT PANEL: Filters ---
        right_panel = QVBoxLayout()
        filters_group = QGroupBox("Filtros")
        filters_layout = QVBoxLayout(filters_group)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        filters = [
            ("Binarização", True),
            ("Escala de Cinza", False),
            ("Filtro de Média", False),
            ("Filtro Mediana", False),
            ("Sobel (Bordas)", False),
            ("Laplaciano", False),
            ("Equalização", False),
            ("Quantização", False)
        ]

        for filter_name, checked in filters:
            rb = QRadioButton(filter_name)
            if checked: rb.setChecked(True)
            scroll_layout.addWidget(rb)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        filters_layout.addWidget(scroll)

        right_panel.addWidget(filters_group)
        main_layout.addLayout(right_panel, 1)

    def load_image(self):  # <-- agora é metodo da classe, não função aninhada
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Escolha uma imagem",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if caminho:
            img = Image.open(caminho)
            img_qt = ImageQt(img)
            pixmap = QPixmap.fromImage(img_qt)

            scaled = pixmap.scaled(
                self.orig_preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.orig_preview_label.setPixmap(scaled)
            self.orig_preview_label.resize(self.orig_preview.size())
            self.orig_preview_label.setText("")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())