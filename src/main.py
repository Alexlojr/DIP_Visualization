import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from src.utils.paths import STYLE_PATH

sys.path.append(str(Path(__file__).parent))

from ui.main_window import MainWindow

def load_qss(app: QApplication) -> None:
    style_path = STYLE_PATH

    if not style_path.exists():
        print(f"Style file not found: {style_path}")
        return

    try:
        with open(style_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Error loading QSS: {e}")


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("PDI Visualizer")

    load_qss(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()