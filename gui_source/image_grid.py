from PyQt5.QtWidgets import QWidget, QScrollArea, QGridLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import QEvent, Qt
from PyQt5 import QtGui
from image_widget import Image_Widget

class Image_Grid(QWidget):
    
    def __init__(self):
        super(Image_Grid, self).__init__()

        layout = QVBoxLayout(self)
        scroller = QScrollArea(self)
        layout.addWidget(scroller)
        contents_widget = QWidget()
        image_grid = QGridLayout(contents_widget)
        contents_widget.setLayout(image_grid)
        self._scroller_contents = contents_widget
        scroller.setWidget(contents_widget)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self._image_grid = image_grid
        self._scroller = scroller

        self.setLayout = layout
        self.setMinimumHeight(500)
        self.setMinimumWidth(800)

        self._target_width = 300

    def add_image(self, image_path):
        widget = Image_Widget(image_path)
        widget.set_width(200)
        widget.parent = self._image_grid
        row = self._image_grid.count() // 5
        column = self._image_grid.count() % 5
        self._image_grid.addWidget(widget, row, column)


    def _resize_rows(self) -> int:
        item_count = self._image_grid.count()
        total_height = 0
        for r in range(self._image_grid.rowCount()):
            max_height = 0
            for c in range(self._image_grid.columnCount()):
                if (r + 1) * (c + 1) <= item_count:
                    item = self._image_grid.itemAtPosition(r, c)
                    if item.widget().height() > max_height:
                        max_height = item.widget().minimumHeight()
            
            self._image_grid.setRowMinimumHeight(r, max_height)
            total_height += max_height
        return total_height
        
            
        
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        target_width = self._scroller.width() // self._image_grid.columnCount()
        for i in range(self._image_grid.count()):
            item = self._image_grid.itemAt(i).widget()
            item.set_width(target_width)

        height = self._resize_rows()

        self._scroller_contents.setFixedWidth(self._scroller.width())
        self._scroller_contents.setFixedHeight(height)

        
        