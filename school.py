from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import sys
from PyQt6.uic import loadUiType

ui,_ = loadUiType('qt_ui/school.ui')

class MainApp(QMainWindow,ui):
	def __init__(self) :
		QMainWindow.__init__(self)
		self.setupUi(self)

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
