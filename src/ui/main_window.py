import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QRadioButton,
    QGroupBox, QFileDialog, QSpinBox, QButtonGroup, QSizePolicy,
    QProgressBar,
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from src.ui.worker import FilterWorker
from PIL import Image
from PIL.ImageQt import ImageQt
from pathlib import Path


class ImagePreview(QWidget):
    """
    Image preview widget that auto-scales on resize.
    Stores the original QPixmap and redraws it centered with preserved aspect ratio.
    """

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self._pixmap: QPixmap | None = None
        self._placeholder = placeholder
        self.setObjectName("imagePlaceholder")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(300, 300)

    def set_image(self, img: Image.Image | None):
        if img is None:
            self._pixmap = None
        else:
            self._pixmap = QPixmap.fromImage(ImageQt(img))
        self.update()

    def paintEvent(self, _event):
        from PySide6.QtGui import QPen
        painter = QPainter(self)

        if self._pixmap is None:
            # Dashed border when no image is loaded
            pen = QPen(QColor("#4a4a6a"))
            pen.setStyle(Qt.DashLine)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            painter.setPen(QColor("#4a4a6a"))
            painter.drawText(self.rect(), Qt.AlignCenter, self._placeholder)
        else:
            scaled = self._pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            x = (self.width()  - scaled.width())  // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

            # Subtle solid border when image is loaded
            pen = QPen(QColor("#333355"))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        painter.end()

FALLBACK_IMAGE_PATH = Path(__file__).resolve().parent.parent / "images" / "test-image.png"

# (label, min, max, default) - label=None disables the spinbox
FILTER_PARAMS = {
    "Binarization":              ("Threshold:",      0,    255,  127),
    "Grayscale":                 (None,              0,    1,    0),
    "Invert Colors":             (None,              0,    1,    0),
    "Histogram Equalization":    (None,              0,    1,    0),
    "Quantization":              ("Levels:",         2,    64,   8),
    "Brightness Adjustment":     ("Brightness:",    -255,  255,  30),
    "Log Transform":             ("Constant c:",     1,    100,  45),
    "Gamma Correction":          ("Gamma (/10):",    1,    30,   10),
    "Mean Filter":               ("Kernel:",         3,    31,   3),
    "Median Filter":             ("Kernel:",         3,    31,   3),
    "Gaussian Filter":           ("Kernel:",         3,    31,   5),
    "Mode Filter":               ("Kernel:",         3,    31,   5),
    "Kuwahara":                  ("Kernel:",         3,    31,   5),
    "Sobel":                     (None,              0,    1,    0),
    "Laplacian":                 (None,              0,    1,    0),
    "Prewitt":                   (None,              0,    1,    0),
    "Sharpen":                   (None,              0,    1,    0),
    # Geometric transformations
    "Rotate 90° CW":             (None,              0,    1,    0),
    "Rotate 90° CCW":            (None,              0,    1,    0),
    "Rotate 180°":               (None,              0,    1,    0),
    "Flip Horizontal":           (None,              0,    1,    0),
    "Flip Vertical":             (None,              0,    1,    0),
    "Upscale":                   ("Factor (x):",     2,    8,    2),
    "Downscale (Pixelation)":    ("Factor (x):",     2,    32,   4),
    "ASCII Art":                 ("Block (px):",     4,    32,   8),
    "Heatmap":                   (None,              0,    1,    0),
    "Glitch":                    ("Intensity:",      1,    30,   8),
    "Dithering":                 ("Levels:",         2,    16,   2),
    "BW Mask":                   (None,              0,    1,    0),
    "Chromatic Aberration":      ("Strength:",       1,    20,   5),
    "Barrel Distortion":         ("Strength:",       1,    50,   15),
    "Ripple":                    ("Amplitude:",      1,    40,   10),
    "Frosted Glass":             ("Radius:",         1,    20,   5),
}


class HistogramWidget(QWidget):
    """Widget that draws a PIL image histogram."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self._channels: list[tuple[list[int], QColor]] = []
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_image(self, image: Image.Image | None):
        self._channels = []
        if image is not None:
            self._channels = self._compute_channels(image)
        self.update()

    @staticmethod
    def _compute_channels(image: Image.Image):
        # Pillow's histogram() is fast (C-level), no manual pixel iteration needed
        mode = image.mode
        if mode not in ("RGB", "L"):
            image = image.convert("RGB")
            mode = "RGB"

        hist = image.histogram()

        if mode == "L":
            return [(hist[:256], QColor(200, 200, 200, 210))]

        return [
            (hist[0:256],   QColor(220, 70,  70,  170)),   # R
            (hist[256:512], QColor(70,  200, 70,  170)),   # G
            (hist[512:768], QColor(70,  120, 220, 170)),   # B
        ]

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        bg = QColor("#1a1a2e")
        painter.fillRect(self.rect(), bg)

        title_h = 18
        padding = 6
        w = self.width() - padding * 2
        h = self.height() - title_h - padding * 2

        # Title
        painter.setPen(QColor("#aaaacc"))
        title_font = QFont()
        title_font.setPointSize(8)
        painter.setFont(title_font)
        painter.drawText(QRect(0, 2, self.width(), title_h), Qt.AlignCenter, self.title)

        if not self._channels:
            painter.setPen(QColor("#555"))
            painter.drawText(
                QRect(padding, title_h, w, h), Qt.AlignCenter, "No image"
            )
            painter.end()
            return

        # Find global max for scaling (skip index 0 to avoid huge DC spike from padding)
        global_max = max(
            max(vals[1:]) for vals, _ in self._channels
        ) or 1

        bar_w = max(1.0, w / 256)
        top = title_h + padding

        painter.setCompositionMode(QPainter.CompositionMode_Plus)

        for vals, color in self._channels:
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            for i, v in enumerate(vals):
                bar_h = int(v / global_max * h)
                if bar_h > 0:
                    x = padding + int(i * bar_w)
                    painter.drawRect(x, top + h - bar_h, max(1, int(bar_w)), bar_h)

        # Subtle border
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.setPen(QColor("#333355"))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(padding, top, w, h)

        painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DIP Visualization - Digital Image Processing")
        self.setMinimumSize(1440, 860)

        self.current_image: Image.Image | None = None
        self.processed_image: Image.Image | None = None
        self._worker: FilterWorker | None = None

        self._setup_ui()
        self._setup_statusbar()

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(12)

        root.addLayout(self._build_left_panel(), 2)
        root.addLayout(self._build_center_panel(), 5)
        root.addLayout(self._build_right_panel(), 2)

    def _build_left_panel(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # File
        file_group = QGroupBox("File")
        fl = QVBoxLayout(file_group)
        self.load_btn = QPushButton("Load Image")
        self.load_btn.setObjectName("primaryBtn")
        self.load_btn.clicked.connect(self.load_image)
        self.save_btn = QPushButton("Save Result")
        self.save_btn.clicked.connect(self.save_image)
        fl.addWidget(self.load_btn)
        fl.addWidget(self.save_btn)
        layout.addWidget(file_group)

        # Info
        info_group = QGroupBox("Image Info")
        il = QVBoxLayout(info_group)
        self.lbl_resolution = QLabel("Resolution: -")
        self.lbl_channels   = QLabel("Mode: -")
        self.lbl_format     = QLabel("Format: -")
        for lbl in (self.lbl_resolution, self.lbl_channels, self.lbl_format):
            lbl.setWordWrap(True)
            il.addWidget(lbl)
        layout.addWidget(info_group)

        # Parameter
        param_group = QGroupBox("Parameter")
        pl = QVBoxLayout(param_group)
        self.param_label = QLabel("—")
        self.param_label.setAlignment(Qt.AlignCenter)
        self.param_input = QSpinBox()
        self.param_input.setRange(0, 255)
        self.param_input.setValue(3)
        self.param_input.setEnabled(False)
        self.param_input.valueChanged.connect(self._on_param_changed)
        pl.addWidget(self.param_label)
        pl.addWidget(self.param_input)
        layout.addWidget(param_group)

        layout.addStretch()
        return layout

    def _build_center_panel(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Image previews
        images_row = QHBoxLayout()
        images_row.setSpacing(10)

        for attr, title in (("orig_preview", "Original Image"),
                            ("proc_preview", "Processed Image")):
            col = QVBoxLayout()
            col.setSpacing(4)
            header = QLabel(title)
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("font-weight: bold; font-size: 11px; color: #aaa;")
            col.addWidget(header)

            preview = ImagePreview(title)
            col.addWidget(preview)
            setattr(self, attr, preview)

            images_row.addLayout(col)

        layout.addLayout(images_row, 3)

        # Histograms
        hist_row = QHBoxLayout()
        hist_row.setSpacing(10)

        self.orig_hist = HistogramWidget("Histogram - Original")
        self.proc_hist = HistogramWidget("Histogram - Processed")
        hist_row.addWidget(self.orig_hist)
        hist_row.addWidget(self.proc_hist)

        layout.addLayout(hist_row, 1)
        return layout

    def _build_right_panel(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        outer = QGroupBox("Filters")
        outer_layout = QVBoxLayout(outer)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(8)

        # QButtonGroup enforces exclusivity across visual groups
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._btn_group.buttonClicked.connect(self._on_filter_selected)

        sections = [
            ("Point Operations", [
                "Binarization",
                "Grayscale",
                "Invert Colors",
                "Histogram Equalization",
                "Quantization",
                "Brightness Adjustment",
                "Log Transform",
                "Gamma Correction",
            ]),
            ("Low-Pass Filters", [
                "Mean Filter",
                "Median Filter",
                "Gaussian Filter",
                "Mode Filter",
                "Kuwahara",
            ]),
            ("High-Pass Filters", [
                "Sobel",
                "Laplacian",
                "Prewitt",
                "Sharpen",
            ]),
            ("Geometric Transformations", [
                "Rotate 90° CW",
                "Rotate 90° CCW",
                "Rotate 180°",
                "Flip Horizontal",
                "Flip Vertical",
                "Upscale",
                "Downscale (Pixelation)",
            ]),
            ("Special Effects", [
                "ASCII Art",
                "Heatmap",
                "Glitch",
                "Dithering",
                "BW Mask",
            ]),
            ("Lens/Glass Distortions", [
                "Chromatic Aberration",
                "Barrel Distortion",
                "Ripple",
                "Frosted Glass",
            ]),
        ]

        for section_title, filters in sections:
            group = QGroupBox(section_title)
            gl = QVBoxLayout(group)
            gl.setSpacing(3)
            for name in filters:
                rb = QRadioButton(name)
                self._btn_group.addButton(rb)
                gl.addWidget(rb)
            cl.addWidget(group)

        cl.addStretch()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
        layout.addWidget(outer)
        return layout

    def _setup_statusbar(self):
        self._status_lbl = QLabel("Ready")
        self._prog_bar = QProgressBar()
        self._prog_bar.setMaximumWidth(200)
        self._prog_bar.setTextVisible(False)
        self._prog_bar.setVisible(False)
        self.statusBar().addWidget(self._status_lbl, 1)
        self.statusBar().addPermanentWidget(self._prog_bar)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose an image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp)"
        )
        if not path:
            path = str(FALLBACK_IMAGE_PATH)

        try:
            img = Image.open(path)
        except Exception as e:
            print(f"Error loading image: {e}. Using fallback image.")
            try:
                img = Image.open(str(FALLBACK_IMAGE_PATH))
            except Exception as e2:
                print(f"Failed to load fallback image: {e2}")
                return

        self._set_original(img)

    def save_image(self):
        if self.processed_image is None:
            return

        from src.utils.paths import IMAGES_DIR
        import os
        os.makedirs(IMAGES_DIR, exist_ok=True)

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", str(IMAGES_DIR),
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        )
        if path:
            self.processed_image.save(path)

    def _on_filter_selected(self, _btn):
        self._apply_filter()

    def _on_param_changed(self):
        self._apply_filter()

    def _apply_filter(self):
        checked = self._btn_group.checkedButton()
        if checked is None:
            return

        selected = checked.text()

        # Update parameter widget
        cfg = FILTER_PARAMS.get(selected)
        if cfg:
            label_text, p_min, p_max, p_default = cfg
            self.param_input.blockSignals(True)
            self.param_input.setRange(p_min, p_max)
            cur = self.param_input.value()
            if cur < p_min or cur > p_max:
                self.param_input.setValue(p_default)
            self.param_input.blockSignals(False)

            has_param = label_text is not None
            self.param_label.setText(label_text if has_param else "—")
            self.param_input.setEnabled(has_param)

        if self.current_image is None:
            self._load_from_path(str(FALLBACK_IMAGE_PATH))
        if self.current_image is None:
            return

        # Cancel previous worker without blocking the UI
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.result_ready.disconnect()
            self._worker.progress.disconnect()

        fn, args, kwargs = self._build_filter_call(selected, self.param_input.value())

        self._worker = FilterWorker(fn, args=args, kwargs=kwargs)
        self._worker.progress.connect(self._on_progress)
        self._worker.result_ready.connect(self._on_result)
        self._worker.start()

        total = self.current_image.width * self.current_image.height
        self._status_lbl.setText(f"Processing {selected}...  0 / {total:,} px")
        self._prog_bar.setMaximum(total)
        self._prog_bar.setValue(0)
        self._prog_bar.setVisible(True)

    def _on_progress(self, done: int, total: int):
        self._prog_bar.setValue(done)
        checked = self._btn_group.checkedButton()
        name = checked.text() if checked else "…"
        self._status_lbl.setText(f"Processing {name}...  {done:,} / {total:,} px")

    def _on_result(self, result):
        self._prog_bar.setVisible(False)
        if result is None:
            self._status_lbl.setText("Error during processing.")
            return

        self.processed_image = result
        self.proc_preview.set_image(result)
        self.proc_hist.set_image(result)

        total = result.width * result.height
        if self.current_image and result.size != self.current_image.size:
            ow, oh = self.current_image.size
            self._status_lbl.setText(
                f"Done - {ow}x{oh} -> {result.width}x{result.height} ({total:,} px)"
            )
        else:
            self._status_lbl.setText(f"Done - {total:,} px processed")

    def _build_filter_call(self, name: str, val: int):
        """Return (fn, args, kwargs) for FilterWorker execution."""
        from src.Algorythms.point_operations import (
            binarization, grayscale, invert_colors,
            histogram_equalization, quantization,
            brightness_adjust, log_transform, gamma_correction,
            apply_bw_mask,
        )
        from src.utils.paths import IMAGES_DIR
        from src.Algorythms.filters import (
            mean_filter, median_filter, gaussian_filter,
            sobel_filter, laplacian_filter, prewitt_filter, sharpen_filter,
            mode_filter, kuwahara_filter,
        )
        from src.Algorythms.transformations import (
            rotate_90cw, rotate_90ccw, rotate_180,
            flip_horizontal, flip_vertical, upscale, downscale,
            ascii_art_filter, heatmap_filter, glitch_filter,
            dither_floyd_steinberg, chromatic_aberration,
            barrel_distortion, ripple_filter, frosted_glass_filter,
        )

        img = self.current_image
        odd_val = max(3, val | 1)

        dispatch = {
            "Binarization":              (binarization,          (img,), {"threshold": val}),
            "Grayscale":                 (grayscale,             (img,), {}),
            "Invert Colors":             (invert_colors,         (img,), {}),
            "Histogram Equalization":    (histogram_equalization,(img,), {}),
            "Quantization":              (quantization,          (img,), {"levels": val}),
            "Brightness Adjustment":     (brightness_adjust,     (img,), {"value": val}),
            "Log Transform":             (log_transform,         (img,), {"c": val}),
            "Gamma Correction":          (gamma_correction,      (img,), {"gamma": val / 10.0}),
            "Mean Filter":               (mean_filter,           (img,), {"kernel_size": odd_val}),
            "Median Filter":             (median_filter,         (img,), {"kernel_size": odd_val}),
            "Gaussian Filter":           (gaussian_filter,       (img,), {"kernel_size": odd_val}),
            "Mode Filter":               (mode_filter,           (img,), {"kernel_size": odd_val}),
            "Kuwahara":                 (kuwahara_filter,       (img,), {"kernel_size": odd_val}),
            "Sobel":                     (sobel_filter,          (img,), {}),
            "Laplacian":                 (laplacian_filter,      (img,), {}),
            "Prewitt":                   (prewitt_filter,        (img,), {}),
            "Sharpen":                   (sharpen_filter,        (img,), {}),
            "Rotate 90° CW":             (rotate_90cw,           (img,), {}),
            "Rotate 90° CCW":            (rotate_90ccw,          (img,), {}),
            "Rotate 180°":               (rotate_180,            (img,), {}),
            "Flip Horizontal":           (flip_horizontal,       (img,), {}),
            "Flip Vertical":             (flip_vertical,         (img,), {}),
            "Upscale":                  (upscale,               (img,), {"factor": val}),
            "Downscale (Pixelation)":    (downscale,             (img,), {"factor": val}),
            "ASCII Art":                 (ascii_art_filter,      (img,), {"block_size": val}),
            "Heatmap":                   (heatmap_filter,        (img,), {}),
            "Glitch":                  (glitch_filter,         (img,), {"intensity": val}),
            "Dithering":               (dither_floyd_steinberg,(img,), {"levels": val}),
            "BW Mask":                   (apply_bw_mask,         (img,), {"mask_path": str(IMAGES_DIR / "bw.png")}),
            "Chromatic Aberration":      (chromatic_aberration,  (img,), {"strength": val}),
            "Barrel Distortion":         (barrel_distortion,     (img,), {"strength": val}),
            "Ripple":                    (ripple_filter,         (img,), {"amplitude": val}),
            "Frosted Glass":             (frosted_glass_filter,  (img,), {"radius": val}),
        }

        entry = dispatch.get(name)
        if entry is None:
            print(f"Filter '{name}' is not implemented.")
            return (lambda **kw: img.copy()), (), {}

        return entry

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_original(self, img: Image.Image):
        self.current_image = img
        self.processed_image = img.copy()

        self.orig_preview.set_image(img)
        self.proc_preview.set_image(img)

        self.orig_hist.set_image(img)
        self.proc_hist.set_image(img)

        w, h = img.size
        self.lbl_resolution.setText(f"Resolution: {w} x {h} px")
        self.lbl_channels.setText(f"Mode: {img.mode}")
        self.lbl_format.setText(f"Format: {img.format or 'N/A'}")

    def _load_from_path(self, path: str):
        try:
            self._set_original(Image.open(path))
        except Exception as e:
            print(f"Failed to load: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
