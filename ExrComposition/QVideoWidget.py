import sys

from PySide2.QtWidgets import *

class QVideoWidget(QWidget):

    def __init__(self, parent = None):
        super(QVideoWidget, self).__init__()
        print("Video Widget Crée")
