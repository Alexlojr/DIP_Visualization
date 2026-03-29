# PDI Visualization

A desktop application for studying and visualizing **Digital Image Processing (PDI)** techniques, built with Python and PySide6.

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.10-41CD52?logo=qt&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## Preview

> Load any image, select a filter from the sidebar, and see the result side-by-side with the original — along with live RGB histograms and a real-time pixel processing counter.

---

## Features

### Point Operations
| Operation | Description |
|---|---|
| Binarization | Converts to black & white using an adjustable threshold |
| Grayscale | ITU-R BT.601 luminance conversion |
| Invert Colors | Image negative |
| Histogram Equalization | Redistributes intensity levels to improve contrast |
| Quantization | Reduces the number of color levels |
| Brightness Adjust | Adds a constant offset to each channel |
| Logarithmic Transform | Enhances detail in dark regions |
| Gamma Correction | Power-law curve (γ < 1 brightens, γ > 1 darkens) |

### Low-Pass Filters
| Filter | Description |
|---|---|
| Mean | Smoothing by neighborhood average |
| Median | Salt-and-pepper noise removal |
| Gaussian | Weighted smoothing with a Gaussian kernel |

### High-Pass Filters
| Filter | Description |
|---|---|
| Sobel | Edge detection via X/Y gradients |
| Laplacian | Edge enhancement using the second derivative |
| Prewitt | Edge detection with uniform weights |
| Sharpening | Laplacian-based detail enhancement kernel |

### Geometric Transformations
| Transformation | Description |
|---|---|
| Rotate 90° CW / CCW | Fixed rotations *(placeholder)* |
| Rotate 180° | *(placeholder)* |
| Free Rotation | Adjustable angle *(placeholder)* |
| Flip Horizontal / Vertical | *(placeholder)* |
| Upscale | Resolution upscaling with LANCZOS4 + Unsharp Mask |

### UI & Architecture
- **Live RGB histograms** for both original and processed images
- **Real-time progress counter** — shows pixels processed while filters run
- **Non-blocking processing** via QThread — UI stays responsive during heavy operations
- Load and save images (PNG, JPEG, BMP, TIFF, WebP)
- Dark theme with automatic image scaling on window resize

---

## Getting Started

### Prerequisites
- Python 3.13+

### Installation

```bash
git clone https://github.com/alexj/PDI_Visualization.git
cd PDI_Visualization

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### Running

```bash
python src/main.py
```

---

## Project Structure

```
PDI_Visualization/
├── src/
│   ├── main.py                    # Entry point
│   ├── Algorythm/
│   │   ├── point_operations.py    # Point operations (pure Python)
│   │   ├── filters.py             # Spatial filters (pure Python)
│   │   └── transformations.py     # Geometric transformations
│   ├── ui/
│   │   ├── main_window.py         # Main window & UI logic
│   │   ├── worker.py              # QThread filter worker
│   │   └── styles.qss             # Qt dark theme stylesheet
│   └── utils/
│       └── paths.py               # Project path definitions
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| PySide6 | 6.10.2 | GUI framework (Qt6) |
| Pillow | 12.1.0 | Image loading, saving, and processing |
| opencv-python | 4.11.0.86 | High-quality upscaling |
| numpy | 2.2.4 | Matrix operations for upscaling |

---

## License

MIT © [Alex Lourenço](https://github.com/Alexlojr) — see [LICENSE](LICENSE) for details.
