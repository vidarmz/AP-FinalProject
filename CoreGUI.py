import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QGuiApplication

from PyQt5 import QtCore

Form = uic.loadUiType(os.path.join(os.getcwd(), "Test2.ui"))[0]


class Matplotlib(Form, QMainWindow):
    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setupUi(self)




app = QApplication(sys.argv)
w = Matplotlib()
w.show()
sys.exit(app.exec_())
