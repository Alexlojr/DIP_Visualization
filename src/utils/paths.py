from pathlib import Path

# project root paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# src paths
SRC_DIR = BASE_DIR / "src"
UI_DIR = SRC_DIR / "ui"
UTILS_DIR = SRC_DIR / "utils"
IMAGES_DIR = SRC_DIR / "images"

# files path
STYLE_PATH = UI_DIR / "styles.qss"

