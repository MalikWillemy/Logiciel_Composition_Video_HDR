import sys
import FocusWidget
import this
import random
import subprocess
import FocusWidget
import QVideoWidget
import settings

from os import listdir
from os.path import isfile, join, splitext
from PIL import Image, ImageQt
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import Slot, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile

from manageEXR import *
from callback import *


def returnFinalImage(window):
    window.rgbf = editorWindow.rgbf

    window.size = editorWindow.size
    window.df = editorWindow.df
    window.aof = editorWindow.aof

    window.checkBox_Depth = editorWindow.checkBox_Depth
    window.checkBox_AO = editorWindow.checkBox_AO

    window.checkBox_Depth.setCheckState(editorWindow.checkBox_Depth.checkState())
    window.checkBox_AO.setCheckState(editorWindow.checkBox_AO.checkState())

    window.doubleSpinBox_DepthMin = editorWindow.doubleSpinBox_DepthMin
    window.doubleSpinBox_DepthMax = editorWindow.doubleSpinBox_DepthMax
    window.doubleSpinBox_AOScale = editorWindow.doubleSpinBox_AOScale
    window.doubleSpinBox_ColorMin = editorWindow.doubleSpinBox_ColorMin
    window.doubleSpinBox_ColorMax = editorWindow.doubleSpinBox_ColorMax
 
    window.doubleSpinBox_DepthMin.setValue(editorWindow.doubleSpinBox_DepthMin.value())
    window.doubleSpinBox_DepthMax.setValue(editorWindow.doubleSpinBox_DepthMax.value())
    window.doubleSpinBox_AOScale.setValue(editorWindow.doubleSpinBox_AOScale.value())
    window.doubleSpinBox_ColorMin.setValue(editorWindow.doubleSpinBox_ColorMin.value())
    window.doubleSpinBox_ColorMax.setValue(editorWindow.doubleSpinBox_ColorMax.value())

    return window

def loadimages():
    # OpenFile
    fileName = QFileDialog.getOpenFileName(editorWindow, "Open EXR Image", "../data", "Image Files (*.exr )")

    if fileName[0] != '':
        # Get Images Float and Store in window
        editorWindow.size, editorWindow.rgbf, editorWindow.df, editorWindow.aof = loadEXR(fileName[0])

        # Set Images
        setColorImage(editorWindow)
        setDepthImage(editorWindow)
        setAOImage(editorWindow)
    
        setFinalImage(editorWindow)
    
def loadImagesFrame():
    # OpenFile
    fileName = QFileDialog.getOpenFileName(editorWindow, "Open EXR Image", "../../../Mitsuba/videos/frames", "Image Files (*.exr )")
    
    if fileName[0] != '':
        # Get Images Float and Store in window
        editorWindow.size, editorWindow.rgbf, editorWindow.df, editorWindow.aof =  loadEXR(fileName[0])

        # Set Images
        setColorImage(editorWindow)
        setDepthImage(editorWindow)
        setAOImage(editorWindow)
    
        setFinalImage(editorWindow)
    
def compileDir():
    # OpenFile
    dirName = QFileDialog.getExistingDirectory(editorWindow, "Open EXR Directory", "../../../Mitsuba/videos/frames")

    if dirName != '':
        onlyfiles = [f for f in listdir(dirName) if isfile(join(dirName, f))]

        for val in onlyfiles:
            filename, file_extension = splitext(val)
            if file_extension == ".exr":

                print("Process : " + val)
                exrtojpg(dirName +"/"+ val, dirName +"/"+ filename + ".png", editorWindow.doubleSpinBox_ColorMin.value(), editorWindow.doubleSpinBox_ColorMax.value(), editorWindow.doubleSpinBox_DepthMin.value(),editorWindow.doubleSpinBox_DepthMax.value(), editorWindow.doubleSpinBox_AOScale.value())

        subprocess.run(["../../../Mitsuba/ffmpeg.exe", '-y', '-framerate', '25', '-i', '../../../Mitsuba/videos/frames/frame_%03d.png', '-b', '10000k', '-pix_fmt', 'yuv420p', '../../../Mitsuba/videos/video.mp4'])


def changeColorImage():
    if hasattr(editorWindow, 'rgbf'):
        setColorImage(editorWindow)
        setFinalImage(editorWindow)
    

def changeDepthImage():
    if hasattr(editorWindow, 'rgbf'):
        setDepthImage(editorWindow)
        setFinalImage(editorWindow)
    

def changeAOImage():
    if hasattr(editorWindow, 'rgbf'):
        setAOImage(editorWindow)
        setFinalImage(editorWindow)


def loadPreset():
    fileName = QFileDialog.getOpenFileName(editorWindow, "Open Presets", "../data/presets", "Presets Files (*.pss )")

    if fileName[0] != '':
        presetfile = open(fileName[0],'r')
        colMin = float(presetfile.readline().strip())
        colMax = float(presetfile.readline().strip())
        depthMin = float(presetfile.readline().strip())
        depthMax = float(presetfile.readline().strip())
        AOScale = float(presetfile.readline().strip())
        cb_depth = bool(presetfile.readline().strip())
        cb_AO = bool(presetfile.readline().strip())

        editorWindow.doubleSpinBox_ColorMin.setValue(colMin)
        editorWindow.doubleSpinBox_ColorMax.setValue(colMax)
        editorWindow.doubleSpinBox_DepthMin.setValue(depthMin)
        editorWindow.doubleSpinBox_DepthMax.setValue(depthMax)
        editorWindow.doubleSpinBox_AOScale.setValue(AOScale)
        editorWindow.checkBox_Depth.setCheckState(Qt.CheckState.Checked)
        editorWindow.checkBox_AO.setCheckState(Qt.CheckState.Checked)

    
def savePreset():
    fileName = QFileDialog.getSaveFileName(mainWindow, "Save Presets", "../data/presets/Sample_XXXX_Size_XXXX.pss", "Presets Files (*.pss )")

    if fileName[0] != '':
        presetfile = open(fileName[0],'w')
        presetfile.write(str(editorWindow.doubleSpinBox_ColorMin.value())+"\n")
        presetfile.write(str(editorWindow.doubleSpinBox_ColorMax.value())+"\n")
        presetfile.write(str(editorWindow.doubleSpinBox_DepthMin.value())+"\n")
        presetfile.write(str(editorWindow.doubleSpinBox_DepthMax.value())+"\n")
        presetfile.write(str(editorWindow.doubleSpinBox_AOScale.value())+"\n")
        presetfile.write(str(editorWindow.checkBox_Depth.isChecked())+"\n")
        presetfile.write(str(editorWindow.checkBox_AO.isChecked())+"\n")


def simulate():
    print("Image Finale ",settings.image)

    print("Image Sans Fog ",settings.imageFogless)
    crop_rectangle = (focusWindow.xDoubleSpinBox.value(), focusWindow.yDoubleSpinBox.value(), focusWindow.sizeDoubleSpinBox.value(), focusWindow.sizeDoubleSpinBox.value())
    crop_imageFogless = settings.imageFogless.crop(crop_rectangle)
    print("Image Sans Fog Rognée ",crop_imageFogless)

    settings.image.paste(crop_imageFogless, (0, 0))

    setFinalImageComposed(focusWindow, settings.image)

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
    editorWindow.button_focus.clicked.connect(focusDialog)
    
    # Ao Parameters
    editorWindow.doubleSpinBox_AOScale.valueChanged.connect(changeAOImage)
    editorWindow.checkBox_AO.stateChanged.connect(changeAOImage)

def connectFuncMain(mainWindow):
    mainWindow.button_editorEXR.clicked.connect(loadEditor)

def connectFuncFocus(focusWindow):
    focusWindow.button_simulate.clicked.connect(simulate)

def focusDialog():
    returnFinalImage(focusWindow)
    setFinalImageWithoutFog(focusWindow)
    setFinalImage(focusWindow)
    focusWindow.exec()
    
def loadEditor():
    editorWindow.exec()

def setTreeView(maiWindow):
    mainWindow.imagesTreeView.setContextMenuPolicy(Qt.CustomContextMenu)
    mainWindow.imagesTreeView.customContextMenuRequested.connect(contextMenu)
    model = QFileSystemModel();
    model.setRootPath("../data")
    mainWindow.imagesTreeView.setModel(model)
    mainWindow.imagesTreeView.setRootIndex(model.index("../data"))

def contextMenu():
    menu = QMenu()
    open = menu.addAction("Open")
    open.triggered.connect(openFile)
    cursor = QCursor()
    menu.exec_(cursor.pos())

def openFile():
        # OpenFile
    fileName = mainWindow.imagesTreeView.model().filePath(mainWindow.imagesTreeView.currentIndex())
    print(fileName)
    if fileName[0] != '':
        # Get Images Float and Store in window
        editorWindow.size, editorWindow.rgbf, editorWindow.df, editorWindow.aof = loadEXR(fileName)

        # Set Images
        setColorImage(editorWindow)
        setDepthImage(editorWindow)
        setAOImage(editorWindow)
    
        setFinalImage(editorWindow)
        loadEditor()

if __name__ == "__main__":
    settings.init()

    app = QApplication(sys.argv)

    ui_focusfile = QFile("depth.ui")
    ui_focusfile.open(QFile.ReadOnly)
    loader = QUiLoader()
    loader.registerCustomWidget(FocusWidget)
    focusWindow = loader.load(ui_focusfile)
    connectFuncFocus(focusWindow)

    ui_editorfile = QFile("interfaceTest.ui")
    ui_editorfile.open(QFile.ReadOnly)
    loader = QUiLoader()
    editorWindow = loader.load(ui_editorfile)
    connectFuncEditor(editorWindow)

    ui_Mainfile = QFile("menu.ui")
    ui_Mainfile.open(QFile.ReadOnly)
    loader = QUiLoader()
    loader.registerCustomWidget(QVideoWidget)
    mainWindow = loader.load(ui_Mainfile)
    setTreeView(mainWindow)
    connectFuncMain(mainWindow)
    ui_Mainfile.close()
    mainWindow.show()

    sys.exit(app.exec_())

