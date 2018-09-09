import os, shutil, sys, platform
import FreeCAD

from PySide import QtGui, QtCore
import PySide.QtGui as QtWidgets

def activeWindow():
    return QtWidgets.QApplication.activeWindow()

def getPresetFolder():
    freecaddir = FreeCAD.getUserAppDataDir()

    return os.path.join(freecaddir, 'ConfigPresets')

def getAvailablePresets(presetFolder):
    if not os.path.exists(presetFolder):
        os.mkdir(presetFolder)

    for root, dirs, files in os.walk(presetFolder):
        return dirs
    
    return []

def promptNewName():
    presetName, okPressed = QtWidgets.QInputDialog.getText(activeWindow(), 'Create new Preset', 'Preset Name')
    
    if okPressed:
	    return presetName

def promptExistingName(items):
    items.append('Create New...')

    presetName, okPressed = QtWidgets.QInputDialog.getItem(activeWindow(), 'Choose Preset', 'Select a Preset from the list', items)
    
    if okPressed:
        return presetName

def createAndStore(presetFolder, presetName):
    presetNameFolder = os.path.join(presetFolder, presetName)

    os.mkdir(presetNameFolder)

    store(presetFolder, presetName)
    createStartCommand(presetNameFolder, presetName)

def store(presetFolder, presetName):
    appdir = FreeCAD.getUserAppDataDir()
    srcSystemconfig = os.path.join(appdir, 'system.cfg')
    srcUserconfig = os.path.join(appdir, 'user.cfg')
    dest = os.path.join(presetFolder, presetName)

    shutil.copy2(srcSystemconfig, dest)
    shutil.copy2(srcUserconfig, dest)

def createStartCommand(presetNameFolder, presetName):
    freeCadExecutable = sys.executable

    linkDirectory = QtWidgets.QFileDialog.getExistingDirectory(activeWindow(), "Symlink Directory");
    userCfg = os.path.join(presetNameFolder, 'user.cfg')
    systemCfg = os.path.join(presetNameFolder, 'system.cfg')

    if platform.system() == 'Windows':
        createBat(linkDirectory, freeCadExecutable, userCfg, systemCfg)
    else:
        createSh(linkDirectory, freeCadExecutable, userCfg, systemCfg)

def createBat(linkDirectory, executable, userCfg, systemCfg):
    linkFilePath = os.path.join(linkDirectory, 'FreeCAD_%s.bat' % (presetName))
    linkFile = open(linkFilePath, 'w')

    try:
        linkFile.write('start "" "%s" --user-cfg "%s" --system-cfg "%s"' % (executable, userCfg, systemCfg))
    finally:
        linkFile.close()

def createSh(linkDirectory, executable, userCfg, systemCfg):
    linkFilePath = os.path.join(linkDirectory, 'FreeCAD_%s.sh' % (presetName))
    linkFile = open(linkFilePath, 'w')

    try:
        linkFile.write('#!/bin/bash\n\n')
        linkFile.write('"%s" --user-cfg "%s" --system-cfg "%s"' % (executable, userCfg, systemCfg))
    finally:
        linkFile.close()


FreeCAD.saveParameter()
presetFolder = getPresetFolder()
availablePresets = getAvailablePresets(presetFolder)

if len(availablePresets) > 0:
    presetName = promptExistingName(availablePresets)

    if presetName == 'Create New...':
        presetName = promptNewName()

        createAndStore(presetFolder, presetName)
    elif presetName is not None:
        store(presetFolder, presetName)
else:
    presetName = promptNewName()

    if presetName is not None:
        createAndStore(presetFolder, presetName)