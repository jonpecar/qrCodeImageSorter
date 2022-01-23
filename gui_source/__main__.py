from tkinter import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from image_widget import Image_Widget
from image_grid import Image_Grid

def main():

    app = QtWidgets.QApplication([])
    test = Image_Grid() #)
    for i in range(15):
        test.add_image(r"C:\Users\Jonat\Pictures\Fan curve 9-1-22.png")
    test.show()
    app.exec_()
    pass

if __name__ == '__main__':
    main()