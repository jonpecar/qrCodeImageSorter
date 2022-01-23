from cgitb import text
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import Qt

class Image_Widget(QWidget):
    
    def __init__(self, image_path : str):

        super(Image_Widget, self).__init__()

        layout = QVBoxLayout(self)

        #Create the image object and add into a label
        self._image_path = image_path
        pixmap = QPixmap(self._image_path)
        self._image = pixmap
        label = QLabel(self)
        self._image_label = label
        label.setPixmap(pixmap)

        layout.addWidget(label)


        text_input = QLineEdit(self)
        self._text_edit = text_input        
        layout.addWidget(text_input)

        self.setLayout(layout)

    def set_width(self, width : int):
        scaled_pixmap = self._image.scaledToWidth(width)
        self._image_label.setPixmap(scaled_pixmap)
        self._image_label.setMinimumSize(scaled_pixmap.size())
        self._text_edit.setFixedWidth(width)
        self.setMinimumHeight(self._image_label.height() + self._text_edit.height())
