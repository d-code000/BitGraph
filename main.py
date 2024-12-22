import sys

from PySide6.QtWidgets import QApplication
from model.graph_widget import GraphWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = GraphWidget()
    window.show()

    sys.exit(app.exec())
