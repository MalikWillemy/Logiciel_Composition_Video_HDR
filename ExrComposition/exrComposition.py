import sys
import random
import subprocess

from os import listdir
from os.path import isfile, join, splitext

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import Slot, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile

from manageEXR import *
from callback import *

def loadimages():
    # OpenFile
    fileName = QFileDialog.getOpenFileName(window, "Open EXR Image", "../data", "Image Files (*.exr )")
    
    if fileName[0] != '':
        # Get Images Float and Store in window
        window.size, window.rgbf, window.df, window.aof =  loadEXR(fileName[0])

        # Set Images
        setColorImage(window)
        setDepthImage(window)
        setAOImage(window)
    
        setFinalImage(window)
    
def loadImagesFrame():
    # OpenFile
    fileName = QFileDialog.getOpenFileName(window, "Open EXR Image", "../../../Mitsuba/videos/frames", "Image Files (*.exr )")
    
    if fileName[0] != '':
        # Get Images Float and Store in window
        window.size, window.rgbf, window.df, window.aof =  loadEXR(fileName[0])

        # Set Images
        setColorImage(window)
        setDepthImage(window)
        setAOImage(window)
    
        setFinalImage(window)
    
def compileDir():
    # OpenFile
    dirName = QFileDialog.getExistingDirectory(window, "Open EXR Directory", "../../../Mitsuba/videos/frames")

    if dirName != '':
        onlyfiles = [f for f in listdir(dirName) if isfile(join(dirName, f))]

        for val in onlyfiles:
            filename, file_extension = splitext(val)
            if file_extension == ".exr":

                print("Process : " + val)
                exrtojpg(dirName +"/"+ val, dirName +"/"+ filename + ".png", window.doubleSpinBox_ColorMin.value(), window.doubleSpinBox_ColorMax.value(), window.doubleSpinBox_DepthMin.value(),window.doubleSpinBox_DepthMax.value(), window.doubleSpinBox_AOScale.value())

        subprocess.run(["../../../Mitsuba/ffmpeg.exe", '-y', '-framerate', '25', '-i', '../../../Mitsuba/videos/frames/frame_%03d.png', '-b', '10000k', '-pix_fmt', 'yuv420p', '../../../Mitsuba/videos/video.mp4'])


def changeColorImage():
    if hasattr(window, 'rgbf'):
        setColorImage(window)
        setFinalImage(window)
    

def changeDepthImage():
    if hasattr(window, 'rgbf'):
        setDepthImage(window)
        setFinalImage(window)
    

def changeAOImage():
    if hasattr(window, 'rgbf'):
        setAOImage(window)
        setFinalImage(window)


def loadPreset():
    fileName = QFileDialog.getOpenFileName(window, "Open Presets", "../data/presets", "Presets Files (*.pss )")

    if fileName[0] != '':
        presetfile = open(fileName[0],'r')
        colMin = float(presetfile.readline().strip())
        colMax = float(presetfile.readline().strip())
        depthMin = float(presetfile.readline().strip())
        depthMax = float(presetfile.readline().strip())
        AOScale = float(presetfile.readline().strip())
        cb_depth = bool(presetfile.readline().strip())
        cb_AO = bool(presetfile.readline().strip())

        window.doubleSpinBox_ColorMin.setValue(colMin)
        window.doubleSpinBox_ColorMax.setValue(colMax)
        window.doubleSpinBox_DepthMin.setValue(depthMin)
        window.doubleSpinBox_DepthMax.setValue(depthMax)
        window.doubleSpinBox_AOScale.setValue(AOScale)
        window.checkBox_Depth.setCheckState(Qt.CheckState.Checked)
        window.checkBox_AO.setCheckState(Qt.CheckState.Checked)

    
def savePreset():
    fileName = QFileDialog.getSaveFileName(window, "Save Presets", "../data/presets/Sample_XXXX_Size_XXXX.pss", "Presets Files (*.pss )")

    if fileName[0] != '':
        presetfile = open(fileName[0],'w')
        presetfile.write(str(window.doubleSpinBox_ColorMin.value())+"\n")
        presetfile.write(str(window.doubleSpinBox_ColorMax.value())+"\n")
        presetfile.write(str(window.doubleSpinBox_DepthMin.value())+"\n")
        presetfile.write(str(window.doubleSpinBox_DepthMax.value())+"\n")
        presetfile.write(str(window.doubleSpinBox_AOScale.value())+"\n")
        presetfile.write(str(window.checkBox_Depth.isChecked())+"\n")
        presetfile.write(str(window.checkBox_AO.isChecked())+"\n")

def connectFuncEditor(editorWindow):
    # File Dir
    editorWindow.button_loadexr.clicked.connect(loadimages)
    editorWindow.button_loadexr_frame.clicked.connect(loadImagesFrame)
    editorWindow.button_compileexr_dir.clicked.connect(compileDir)

    # Presets
    editorWindow.button_save_preset.clicked.connect(savePreset)
    editorWindow.button_load_preset.clicked.connect(loadPreset)
    
    # RGB parameters
    editorWindow.doubleSpinBox_ColorMin.valueChanged.connect(changeColorImage)
    editorWindow.doubleSpinBox_ColorMax.valueChanged.connect(changeColorImage)

    # Depth parameters
    editorWindow.doubleSpinBox_DepthMin.valueChanged.connect(changeDepthImage)
    editorWindow.doubleSpinBox_DepthMax.valueChanged.connect(changeDepthImage)
    editorWindow.checkBox_Depth.stateChanged.connect(changeDepthImage)
    
    # Ao Parameters
    editorWindow.doubleSpinBox_AOScale.valueChanged.connect(changeAOImage)
    editorWindow.checkBox_AO.stateChanged.connect(changeAOImage)

def loadEditor():
    ui_editorfile = QFile("interfaceTest.ui")
    ui_editorfile.open(QFile.ReadOnly)
    loader = QUiLoader()
    editorWindow = loader.load(ui_editorfile)

    connectFuncEditor(editorWindow)
    
    editorWindow.exec()

def connectFuncMain(mainWindow):
    mainWindow.button_editorEXR.clicked.connect(loadEditor)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui_Mainfile = QFile("menu.ui")
    ui_Mainfile.open(QFile.ReadOnly)


    loader = QUiLoader()
    mainWindow = loader.load(ui_Mainfile)

    connectFuncMain(mainWindow)
    
    ui_Mainfile.close()
    mainWindow.show()

    sys.exit(app.exec_())

