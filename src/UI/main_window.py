import sys

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QHBoxLayout, QMessageBox, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def setupUi(self):









if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()