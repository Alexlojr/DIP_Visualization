# DIP Visualization

A desktop application for studying and visualizing **Digital Image Processing (DIP)** techniques, built with Python and PySide6.

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
| Brightness Adjustment | Adds a constant offset to each channel |
| Log Transform | Enhances detail in dark regions |
| Gamma Correction | Power-law curve (γ < 1 brightens, γ > 1 darkens) |
| BW Mask | Applies `src/images/bw.png`: white keeps original pixels, black outputs black |

### Low-Pass Filters
| Filter | Description |
|---|---|
| Mean Filter | Smoothing by neighborhood average |
| Median Filter | Salt-and-pepper noise removal |
| Gaussian Filter | Weighted smoothing with a Gaussian kernel |
| Mode Filter | Replaces each neighborhood with its modal value |
| Kuwahara | Edge-preserving smoothing by regional variance selection |

### High-Pass Filters
| Filter | Description |
|---|---|
| Sobel | Edge detection via X/Y gradients |
| Laplacian | Edge enhancement using the second derivative |
| Prewitt | Edge detection with uniform weights |
| Sharpen | Laplacian-based detail enhancement kernel |

### Geometric Transformations
| Transformation | Description |
|---|---|
| Rotate 90° CW | 90-degree clockwise rotation |
| Rotate 90° CCW | 90-degree counter-clockwise rotation |
| Rotate 180° | 180-degree rotation |
| Flip Horizontal | Mirrors the image along the vertical axis |
| Flip Vertical | Mirrors the image along the horizontal axis |
| Upscale | OpenCV-based upscaling with LANCZOS4 + denoise + unsharp + CLAHE |
| Downscale (Pixelation) | Degradation pipeline with blur, downsample, nearest upscale, and noise |

### Special Effects
| Effect | Description |
|---|---|
| ASCII Art | Converts the image into text-like block rendering |
| Heatmap | Maps luminance values to a thermal color gradient |
| Glitch | Simulates digital signal corruption artifacts |
| Dithering | Floyd-Steinberg error diffusion quantization |
| BW Mask | Applies grayscale mask composition from `src/images/bw.png` |

### Lens / Glass Distortions
| Effect | Description |
|---|---|
| Chromatic Aberration | Radial RGB channel separation with bilinear sampling |
| Barrel Distortion | Fisheye-style radial distortion with bilinear sampling |
| Ripple | Wave displacement using sinusoidal offsets |
| Frosted Glass | Random local pixel scattering to simulate textured glass |

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
| opencv-python | 4.11.0.86 | Geometric resampling and enhancement pipeline support |
| numpy | 2.2.4 | Numeric arrays used by OpenCV-based operations |

---

## License

MIT © [Alex Lourenço](https://github.com/Alexlojr) — see [LICENSE](LICENSE) for details.
