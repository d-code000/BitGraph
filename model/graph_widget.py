import uuid
from typing import Union, Optional, TypeVar

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ui.migration.graph import Ui_MainWindow

T = TypeVar('T')


class GraphWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        layout_canvas = QVBoxLayout(self.ui.matplotlibWidget)

        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout_canvas.addWidget(canvas)
        layout_canvas.addWidget(NavigationToolbar(canvas, self))

        self.ui.addPushButton.clicked.connect(self.add_func_line)

        for widget in self.get_func_line():
            widget.setVisible(False)

        self.add_func_line()

    def find_by_uuid(self, object_uuid: str, object_type: type[T]) -> Optional[T]:
        for i in range(self.ui.graphListVerticalLayout.count()):
            layout_item = self.ui.graphListVerticalLayout.itemAt(i)
            if object_uuid in layout_item.objectName():
                for j in range(layout_item.count()):
                    widget = layout_item.itemAt(j).widget()
                    if isinstance(widget, object_type):
                        return widget
        return None

    def get_func_line(self) -> tuple[QWidget, ...]:
        widgets = []
        for i in range(self.ui.graphItemParentHorizontalLayout.count()):
            item = self.ui.graphItemParentHorizontalLayout.itemAt(i)
            widget = item.widget()
            widgets.append(widget)
        return tuple(widgets)

    def add_func_line(self) -> str:
        objects_id = str(uuid.uuid4())
        new_layout = QHBoxLayout()
        new_layout.setObjectName(self.ui.graphItemParentHorizontalLayout.objectName() + "_" + objects_id)
        for widget in self.get_func_line():
            new_widget: Union[QLabel, QLineEdit, QPushButton] = widget.__class__(widget)
            new_widget.setObjectName(widget.objectName() + "_" + objects_id)
            new_widget_name = new_widget.objectName()

            new_widget.setFont(widget.font())

            if isinstance(widget, QLabel):
                new_widget.setText(widget.text())

            if isinstance(widget, QPushButton):
                new_widget.setText(widget.text())
                new_widget.setIcon(widget.icon())
                new_widget.setIconSize(widget.iconSize())
                if "plot" in new_widget_name:
                    new_widget.clicked.connect(self.plot_func_line)
                elif "copy" in new_widget_name:
                    new_widget.clicked.connect(self.copy_func_line)
                elif "delete" in new_widget_name:
                    new_widget.clicked.connect(self.delete_func_line)

            new_layout.addWidget(new_widget)

        self.ui.graphListVerticalLayout.addLayout(new_layout)
        return objects_id

    def copy_func_line(self):
        object_id = self.sender().objectName().split("_")[-1]
        new_object_id = self.add_func_line()
        line_edit = self.find_by_uuid(object_id, QLineEdit)
        new_line_edit = self.find_by_uuid(new_object_id, QLineEdit)
        new_line_edit.setText(line_edit.text())

    def delete_func_line(self):
        sender = self.sender()
        for i in range(self.ui.graphListVerticalLayout.count()):
            layout_item = self.ui.graphListVerticalLayout.itemAt(i)
            if isinstance(layout_item, QHBoxLayout):
                layout = layout_item.layout()
                for j in range(layout.count()):
                    widget = layout.itemAt(j).widget()
                    if widget and widget == sender:
                        while layout.count():
                            child = layout.takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                        self.ui.graphListVerticalLayout.removeItem(layout_item)
                        return
    
    def plot_func_line(self):
        pass
