import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSlider, QScrollArea, QRadioButton,
    QGroupBox, QSizePolicy, QFileDialog, QSpinBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont, QColor, QPalette
from PIL import Image
from PIL.ImageQt import ImageQt
from pathlib import Path

# Fix fallback image path
FALLBACK_IMAGE_PATH = Path(__file__).resolve().parent.parent / "Algorythm" / "test-image.jpg"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDI Visualization - Processamento Digital de Imagens")
        self.setMinimumSize(1200, 800)

        self.current_image = None
        self.processed_image = None

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
        self.save_btn.clicked.connect(self.save_image)
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.save_btn)
        left_panel.addWidget(file_group)

        info_group = QGroupBox("Informações")
        info_layout = QVBoxLayout(info_group)
        self.lbl_resolution = QLabel("Resolução: N/A")
        self.lbl_channels = QLabel("Canais: N/A")
        self.lbl_format = QLabel("Formato: N/A")
        info_layout.addWidget(self.lbl_resolution)
        info_layout.addWidget(self.lbl_channels)
        info_layout.addWidget(self.lbl_format)
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

        # Parameter Input Middle
        param_layout = QVBoxLayout()
        param_layout.addWidget(QLabel("Parâmetro:"))
        self.param_input = QSpinBox()
        self.param_input.setRange(0, 255)  # Keep the range 0-255 allowing thresholds up to 255
        self.param_input.setValue(3)  # Better default to prevent accidental billion operations on average spatial filters
        self.param_input.valueChanged.connect(self.update_parameter)
        param_layout.addWidget(self.param_input)
        param_layout.addStretch()
        images_layout.addLayout(param_layout)

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

        # Operations (Point)
        lbl_ops = QLabel("<b>Operações Pontuais</b>")
        scroll_layout.addWidget(lbl_ops)
        
        point_ops = [
            ("Binarização", False),
            ("Escala de Cinza", False),
            ("Equalização", False),
            ("Quantização", False),
            ("Inverter Cores", False)
        ]

        self.radio_buttons = []
        for op_name, checked in point_ops:
            rb = QRadioButton(op_name)
            if checked: rb.setChecked(True)
            rb.toggled.connect(self.apply_filter)
            scroll_layout.addWidget(rb)
            self.radio_buttons.append(rb)
            
        scroll_layout.addSpacing(15)

        # Filters (Spatial)
        lbl_filters = QLabel("<b>Filtros (Espaciais)</b>")
        scroll_layout.addWidget(lbl_filters)
        
        spatial_filters = [
            ("Filtro de Média", False),
            ("Filtro Mediana", False),
            ("Sobel (Bordas)", False),
            ("Laplaciano", False)
        ]

        for filter_name, checked in spatial_filters:
            rb = QRadioButton(filter_name)
            if checked: rb.setChecked(True)
            rb.toggled.connect(self.apply_filter)
            scroll_layout.addWidget(rb)
            self.radio_buttons.append(rb)

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

        if not caminho:
            caminho = str(FALLBACK_IMAGE_PATH)

        try:
            img = Image.open(caminho)
        except Exception as e:
            print(f"Error loading image: {e}. Falling back to default image.")
            try:
                img = Image.open(str(FALLBACK_IMAGE_PATH))
            except Exception as inner_e:
                print(f"Failed to load fallback image: {inner_e}")
                return
                
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

        self.proc_preview_label.setPixmap(scaled)
        self.proc_preview_label.resize(self.proc_preview.size())
        self.proc_preview_label.setText("")
        
        self.current_image = img
        self.processed_image = img.copy()

        width, height = img.size
        self.lbl_resolution.setText(f"Resolução: {width}x{height}")
        self.lbl_channels.setText(f"Canais: {img.mode}")
        if hasattr(img, 'format') and img.format:
            self.lbl_format.setText(f"Formato: {img.format}")
        else:
            self.lbl_format.setText("Formato: N/A")

    def save_image(self):
        if self.processed_image is None:
            return
            
        from src.utils.paths import IMAGES_DIR
        import os
        
        os.makedirs(IMAGES_DIR, exist_ok=True)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Imagem",
            str(IMAGES_DIR),
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.processed_image.save(file_path)

    def apply_filter(self):
        selected_filter = None
        for rb in getattr(self, 'radio_buttons', []):
            if rb.isChecked():
                selected_filter = rb.text()
                break
        
        if selected_filter:
            # Dynamically adjust the default slider value based on the chosen filter
            # We block signals so this doesn't recursively trigger apply_filter again
            self.param_input.blockSignals(True)
            if selected_filter == "Binarização" and self.param_input.value() < 10:
                self.param_input.setValue(127)
            elif selected_filter in ["Filtro de Média", "Filtro Mediana"] and self.param_input.value() > 50:
                self.param_input.setValue(3)
            self.param_input.blockSignals(False)

            if self.current_image is None:
                print("No image loaded. Loading fallback image.")
                self.load_image_from_path(str(FALLBACK_IMAGE_PATH))

            if self.current_image is not None:
                from src.Algorythm.point_operations import binarization, grayscale, invert_colors
                from src.Algorythm.filters import mean_filter, median_filter
                
                if selected_filter == "Binarização":
                    self.processed_image = binarization(self.current_image, self.param_input.value())
                elif selected_filter == "Escala de Cinza":
                    self.processed_image = grayscale(self.current_image)
                elif selected_filter == "Inverter Cores":
                    self.processed_image = invert_colors(self.current_image)
                elif selected_filter == "Filtro de Média":
                    # Certificar que o kernel_size é ímpar e pelo menos 3
                    k_size = max(3, self.param_input.value() | 1)
                    self.processed_image = mean_filter(self.current_image, kernel_size=k_size)
                elif selected_filter == "Filtro Mediana":
                    # Certificar que o kernel_size é ímpar e pelo menos 3
                    k_size = max(3, self.param_input.value() | 1)
                    self.processed_image = median_filter(self.current_image, kernel_size=k_size)
                else:
                    print(f"Filter {selected_filter} not yet implemented.")
                    self.processed_image = self.current_image.copy()
                    
                # Update the processed preview UI
                if self.processed_image:
                    img_qt = ImageQt(self.processed_image)
                    pixmap = QPixmap.fromImage(img_qt)
                    scaled = pixmap.scaled(
                        self.proc_preview.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.proc_preview_label.setPixmap(scaled)
                    
    def load_image_from_path(self, caminho):
        try:
            img = Image.open(caminho)
        except Exception:
            return

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

        # Auto load in the processed preview as well
        self.proc_preview_label.setPixmap(scaled)
        self.proc_preview_label.resize(self.proc_preview.size())
        self.proc_preview_label.setText("")
        
        self.current_image = img
        self.processed_image = img.copy()

        width, height = img.size
        self.lbl_resolution.setText(f"Resolução: {width}x{height}")
        self.lbl_channels.setText(f"Canais: {img.mode}")
        if hasattr(img, 'format') and img.format:
            self.lbl_format.setText(f"Formato: {img.format}")
        else:
            self.lbl_format.setText("Formato: N/A")

    def update_parameter(self, value):
        print(f"Parameter updated to: {value}")
        self.apply_filter()  # Will re-apply the current filter with new parameter


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())