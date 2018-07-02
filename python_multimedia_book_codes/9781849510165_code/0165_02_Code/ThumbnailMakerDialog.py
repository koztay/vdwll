#-------------------------------------------------------------------------------
# @author: Ninad Sathaye
# @copyright: 2009-2010, Ninad Sathaye email:ninad.consult@gmail.com.
# @license: This program is free software: you can redistribute it and/or modify
#           it under the terms of the GNU General Public License as published by
#           the Free Software Foundation, either version 3 of the License, or
#           (at your option) any later version.
#
#           This program is distributed in the hope that it will be useful,
#           but WITHOUT ANY WARRANTY; without even the implied warranty of
#           MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#           GNU General Public License for more details.
#
#           You should have received a copy of the GNU General Public License
#           along with this program.  If not, see <http://www.gnu.org/licenses/>.
# @summary:
#    This is a Thumbnail Maker utility created for Chapter 2 Project of the
#    book: "Python Multimedia Applications Beginners Guide" ( Packt Publishing )
#    ISBN: [978-1-847190-16-5]
#
#    *Running the Application:
#      This application can be run from command prompt as :
#          $python  ThumbnailMakerDialog.py
#      The following packages need to be installed on your machine
#         - Python 2.6.4
#         - PyQt v 4.6.2 ( for Python 2.6)
#         - PIL  v 1.1.6 (for Python 2.6)
#         - Refer to the book mentioned above for further details about
#           other dependencies.
#      This application is tested only on Windows XP.
#
#      When run, it shows a QDialog called "Thumbnail Maker"
#      This Thumbnail Maker has two sections:
#      1. A control area where you can specify certain image parameters
#         along with options for input and output paths.
#      2. A graphics area on the right hand side where you can view
#         the generated image.
#       This application takes an image file as an input. It processes user
#       specified image parameters such as image pixel dimensions, filter for
#       resampling, rotation angle in degrees etc. The processed image is
#       saved at a location given by the user in a specified output image
#       format.

#      - The class ThumbnailMakerDialog defined in this file is responsible
#        for handling all UI related methods. It delegates UI element and layout
#        code to class UI_ThumbnailMakerDialog. Whereas, the pure main image
#        processing work is done by class  ThumbnailMaker.
#
#Other files:
# Ui_ThumbnailMaker.py : Defines the UI elements. It is generated from
# a file thumbnailMaker.ui using pyuic4 utility of PyQt4.
# ThumbnailMaker.py: This class does the actual image processing.
#-------------------------------------------------------------------------------


from PyQt4.QtGui import QDialog
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QApplication
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QFileDialog
from PyQt4.Qt import QGraphicsScene
from PyQt4.Qt import QGraphicsView
from PyQt4.Qt import QPixmap
from PyQt4.Qt import QMessageBox

from Ui_ThumbnailMakerDialog import Ui_ThumbnailMakerDialog
from ThumbnailMaker   import ThumbnailMaker

import os, sys

class ThumbnailMakerDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        # Define the instance that handles all the
        # Image processing functionality.
        self._thumbnailMaker = ThumbnailMaker(self)

        # Define the instance to access the the UI elements defined in
        # class Ui_ThumbnailMakerDialog.
        self._dialog = Ui_ThumbnailMakerDialog()
        self._dialog.setupUi(self)
        self._dialog.retranslateUi(self)

        # Initialize some other variables.
        self._filePath = ''
        self._dirPath = ''

        # Aspect ratio checkbox is checked by default.
        self.maintainAspectRatio = True

        #Graphics scene for right hand panel.
        # see self._previiewImage() for details.
        self._graphicsScene = QGraphicsScene()

        # Connect slots with signals.
        self._connect()

        # Show the dialog.
        self.show()


    #---------------------------------------------------------------------------
    # START  Some get* methods called by ThumbnailMaker instance
    # (self._thumbnailMaker)
    #---------------------------------------------------------------------------

    def getImageFilterIndex(self):
        """
        Returns the current index of the image filter in the Thumbnail
        Maker dialog. This filter is further used for image resampling.
        @see: ThumbnailMaker.getImageFiter where this is called.
        """
        imageFilterIndex = self._dialog.imageFiltersComboBox.currentIndex()
        return imageFilterIndex

    def getSize(self):
        """
        Returns the image dimensions in pixels.
        It returns a tuple (width, height)
        @see: ThumbnailMaker._resizeImage() where it is called
        """
        widthStr = self._dialog.widthLineEdit.text()
        width = int(widthStr)
        heightStr = self._dialog.heightLineEdit.text()
        height = int(heightStr)
        return (width, height)

    def getAngle(self):
        """
        Return the angle (in degrees) by which the image
        will be rotated. This value is specified in the ThumbailMaker
        dialog.
        @see: ThumbnailMaker.processImage() where it is called
        """
        angle = self._dialog.rotationAngleSpinBox.value()
        return angle

    def getInputImagePath(self):
        """
        Return the full path of the input image file.
        @see: ThumbnailMaker.processImage() where it is called
        """
        return self._filePath


    def getOutImagePath(self):
        """
         Determine and return the full path of the output image.
         @see: ThumbnailMaker.processImage() where it is called
        """

        format = self._dialog.fileFormatComboBox.currentText()
        format = str(format)

        dir, fil = os.path.split(self._filePath)
        fil, ext = os.path.splitext(fil)

        fullPath = os.path.join(self._dirPath, fil + format)
        fullPath = os.path.normpath(fullPath)

        return fullPath

    def getSize(self):
        """
        Returns the image dimensions in pixels.
        It returns a tuple (width, height)
        @see: ThumbnailMaker._resizeImage()
        """
        widthStr = self._dialog.widthLineEdit.text()
        width = int(widthStr)
        heightStr = self._dialog.heightLineEdit.text()
        height = int(heightStr)
        return (width, height)

    #---------------------------------------------------------------------------
    #  END  Some get* methods called by ThumbnailMaker instance
    # (self._thumbnailMaker)
    #---------------------------------------------------------------------------

    def _connect(self):
        """
        Connect slots with signals.
        """
        self.connect(self._dialog.inputFileDialogButton,
        SIGNAL("clicked()"), self._openFileDialog)

        self.connect(self._dialog.outputLocationDialogButton,
        SIGNAL("clicked()"), self._outputLocationPath)

        self.connect(self._dialog.okPushButton,
        SIGNAL("clicked()"), self._processImage)

        self.connect(self._dialog.closePushButton,
        SIGNAL("clicked()"), self.close)

        self.connect(self._dialog.aspectRatioCheckBox,
                       SIGNAL('stateChanged(int)'),
                       self._aspectRatioOptionChanged)

    def _openFileDialog(self):
        """
        Opens the QFileDialog for accepting user input
        for the input image file path (self._filePath)
        """

        self._filePath = (
            str(QFileDialog.getOpenFileName(
                self, "Open Image Path",
                "", "Image file (*.jpg);;All Files (*.*);;")) )
        self._filePath = os.path.normpath(self._filePath)
        self._dialog.inputLineEdit.setText(self._filePath)

    def _outputLocationPath(self):
        """
        Opens QFileDialog so that user can specify the output
        directory location. The result is stored in self._dirPath.
        """

        self._dirPath = (
            str(QFileDialog.getExistingDirectory(
                self,
                "Open Directory",
                "",
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
				)

        self._dirPath = os.path.normpath(self._dirPath)

        self._dialog.outputLineEdit.setText(self._dirPath)

    def _aspectRatioOptionChanged(self, isChecked):
        """
        Method called whenever the state of the checkbox
        "Maintain Aspect ratio" changes.
        """
        self.maintainAspectRatio = isChecked

    def _processImage(self):
        """
        Call the methods of ThumbnailMaker instance to
        process the image. The resultant image is then displayed in
        the graphics pane on the right hand side of the dialog.
        @see: ThumbnailMaker.processImage()
        @see: self._previewImage()
        """

        outFilePath = self.getOutImagePath()

        #-------------------------------------------------------------
        # If we don't want to allow users to overwrite an existing image.
        # You can simply uncomment the following block of code!
        # This is one of the items in "Have a go hero" section of
        # the Thumbnail Maker project.

##        if os.path.exists(outFilePath):
##            msg = "File exists. Please specify a different name."
##            QMessageBox.warning( self, "File exists", \
##                                 msg, QMessageBox.Ok)
##            return
        #-------------------------------------------------------------

        # Process the image and save the file.
        self._thumbnailMaker.processImage()

        # the above line of code should have written this new file.
        # Program will stop here if the file doesn't exist.
        assert os.path.exists(outFilePath)

        #Show the saved image in the graphics area
        self._previewImage(outFilePath)

    def _previewImage(self, path = ''):
        """
        Displays the image in the Graphics area.
        @see: self._processImage()
        """
        # This should never happen. Lets play safe if caller
        # to this method makes a mistake!
        if not path:
            path = self._filePath

        graphicsView = self._dialog.graphicsView
        graphicsScene = self._graphicsScene
        graphicsScene.clear()
        graphicsScene.addPixmap(QPixmap(path))

        graphicsView.setScene(graphicsScene)
        graphicsView.show()


#----------------------------------
# Run the Thumbnail Maker utility!
#----------------------------------
app = QApplication(sys.argv)
tmaker = ThumbnailMakerDialog()
app.exec_()




