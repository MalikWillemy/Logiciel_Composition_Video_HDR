import sys

from PySide2.QtWidgets import *

class FocusWidget(QLabel):

    def mousePressEvent(self, event):
        print("oui")


