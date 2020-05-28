
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import Slot, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile

from manageEXR import *


# Set Color Image
def setColorImage(window):

    image_rgb8 = getRGB8Image(window.rgbf,window.doubleSpinBox_ColorMin.value(),window.doubleSpinBox_ColorMax.value())
    image = image_rgb8.convert("RGB")
    data = image.tobytes("raw","RGB")
    window.label_color.setPixmap(QPixmap.fromImage(QImage(data, window.size[0], window.size[1], QImage.Format_RGB888).scaled(320,180)))
    
    
# Set Depth Image
def setDepthImage(window):

    image_d8 = getD8Image(window.df,window.checkBox_Depth.isChecked(),window.doubleSpinBox_DepthMin.value(),window.doubleSpinBox_DepthMax.value())
    image = image_d8.convert("RGB")
    data = image.tobytes("raw","RGB")
    window.label_depth.setPixmap(QPixmap.fromImage(QImage(data, window.size[0], window.size[1], QImage.Format_RGB888).scaled(320,180)))
    
    
# Set Color Image
def setAOImage(window):

    image_ao8 = getAO8Image(window.aof, window.checkBox_AO.isChecked(),window.doubleSpinBox_AOScale.value())
    image = image_ao8.convert("RGB")
    data = image.tobytes("raw","RGB")
    window.label_AO.setPixmap(QPixmap.fromImage(QImage(data, window.size[0], window.size[1], QImage.Format_RGB888).scaled(320,180)))
   
    
# Set Final Image
def setFinalImage(window):
    
    image_final = getFinalImage(window.rgbf,window.checkBox_Depth.isChecked(),window.df,window.doubleSpinBox_DepthMin.value(),window.doubleSpinBox_DepthMax.value(),window.checkBox_AO.isChecked(),window.aof,window.doubleSpinBox_AOScale.value())#↕,window.checkBox_BlueBG.isChecked())
    image_rgb8 = getRGB8Image(image_final,window.doubleSpinBox_ColorMin.value(),window.doubleSpinBox_ColorMax.value())
    image = image_rgb8.convert("RGB")
    data = image.tobytes("raw","RGB")
    window.label_imagefinal.setPixmap(QPixmap.fromImage(QImage(data, window.size[0], window.size[1], QImage.Format_RGB888)))
