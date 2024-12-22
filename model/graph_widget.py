import uuid
from typing import Union, Optional, TypeVar

import numpy
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from sympy import sympify, lambdify, symbols

from ui.migration.graph import Ui_MainWindow

T = TypeVar('T')


class GraphWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        layout_canvas = QVBoxLayout(self.ui.matplotlibWidget)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.axes = self.canvas.figure.subplots()
        layout_canvas.addWidget(self.canvas)
        layout_canvas.addWidget(NavigationToolbar(self.canvas, self))

        self.ui.addPushButton.clicked.connect(self.add_func_line)
        self.ui.clearPushButton.clicked.connect(self.clear_canvas)
        self.ui.clearAction.triggered.connect(self.clear_canvas)
        self.ui.showHideAction.triggered.connect(self.show_func_lines)
        self.ui.dockWidget.topLevelChanged.connect(self.on_dock_widget_floating)

        for widget in self.get_func_line():
            widget.setVisible(False)

        self.add_func_line()

    def on_dock_widget_floating(self, floating):
        if floating:
            self.ui.dockWidget.resize(300, 0)

    def find_by_uuid(self, object_uuid: str, object_type: type[T]) -> Optional[T]:
        for i in range(self.ui.graphListVerticalLayout.count()):
            layout_item = self.ui.graphListVerticalLayout.itemAt(i)
            if object_uuid in layout_item.objectName():
                for j in range(layout_item.count()):
                    widget = layout_item.itemAt(j).widget()
                    if isinstance(widget, object_type):
                        return widget
        return None

    def show_func_lines(self) -> None:
        if self.ui.dockWidget.isVisible():
            self.ui.dockWidget.hide()
        else:
            self.ui.dockWidget.show()

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

    def plot_func_line(self):

        # TODO: add any input data validation

        objects_id = self.sender().objectName().split("_")[-1]
        line_edit = self.find_by_uuid(objects_id, QLineEdit)

        x_min, x_max, x_count = [-10, 10, 1000]
        y_min, y_max = [-10, 10]

        x_range = self.ui.xRangeLineEdit.text().split(',') if self.ui.xRangeLineEdit.text() else []
        y_range = self.ui.yRangeLineEdit.text().split(',') if self.ui.yRangeLineEdit.text() else []

        if len(x_range) == 1:
            x_count = int(x_range[0])
        elif len(x_range) == 2:
            x_min = int(x_range[0])
            x_max = int(x_range[1])
            if x_min > x_max:
                x_min, x_max = x_max, x_min
        elif len(x_range) == 3:
            x_min = int(x_range[0])
            x_max = int(x_range[1])
            x_count = int(x_range[2])
            if x_min > x_max:
                x_min, x_max = x_max, x_min
            if x_count < 0:
                x_count = -x_count

        if len(y_range) == 1:
            y_min = int(y_range[0])
            y_max = y_min + 10
        elif len(y_range) == 2:
            y_min = int(y_range[0])
            y_max = int(y_range[1])
            if x_min > x_max:
                x_min, x_max = x_max, x_min

        x = symbols('x')
        func_str = line_edit.text().lower()
        func_str = func_str.replace("ctg", "1/tan")
        func_str = func_str.replace("tg", "tan")
        expr = sympify(func_str)

        func = lambdify(x, expr, modules=["numpy"])
        x_vals = numpy.linspace(x_min, x_max, x_count)
        y_vals = func(x_vals)

        valid_mask_y = (y_vals >= y_min) & (y_vals <= y_max)
        x_vals = x_vals[valid_mask_y]
        y_vals = y_vals[valid_mask_y]

        self.axes.plot(x_vals, y_vals, label=f"y = {line_edit.text()}")

        self.axes.axhline(0, color='black', linewidth=1, linestyle='--')
        self.axes.axvline(0, color='black', linewidth=1, linestyle='--')

        self.axes.set_xlim([x_min, x_max])
        self.axes.set_ylim([y_min, y_max])

        self.axes.grid(True)
        self.axes.legend()
        self.canvas.draw()

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

    def clear_canvas(self):
        self.axes.clear()
        self.canvas.draw()
