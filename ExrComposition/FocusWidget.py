import sys

from PySide2.QtWidgets import *

class FocusWidget(QWidget):

    def mousePressEvent(self, event):
        print("oui")

    def __init__(self, parent = None):
        super(FocusWidget, self).__init__()
        print("Focus Widget Crée")