#-------------------------------------------------------------------------------
# @author: Ninad Sathaye
# @copyright: 2010, Ninad Sathaye email:ninad.consult@gmail.com.
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
#    -  A simple GUI based Video player program that uses QT Phonon multimedia
#       framework.
#    -  It is created as an illustration for:
#       Chapter 8 section "Project : GUI Based Video Player"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#
# Dependencies
#---------------
#  In order to run the program the following packages need to be installed and
#  appropriate environment variables need to be set (if it is not done by the
#  installer automatically.)
# 1. Python 2.6
# 2. PyQt4 version 4.6.2 or later for Python 2.6
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
#   Also note that the Ui_VideoPlayerDialog.py is generated from
#   file Ui_VideoPlayer.ui using the pyuic4 utility of PyQt4
#
# *Running the program:
#  Put this file along with Ui_VideoPlayerDialog.py in the same
#  directory and then run the program as
#
#  $python VideoPlayerDialog.py
#
#  The video player GUI window will appear. Open any supported audio or video
#  file and click on Play button to begin the playback.
#-------------------------------------------------------------------------------
from Ui_VideoPlayerDialog import Ui_VideoPlayerDialog

from PyQt4.Qt import QMainWindow
from PyQt4.Qt import QApplication
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QFileDialog
from PyQt4.Qt import QIcon
from PyQt4.Qt import QAction
from PyQt4 import phonon
from PyQt4.phonon import Phonon

import os, sys

class VideoPlayerDialog(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.mediaSource = None
        self.audioPath = ''

        # Initialize some other variables.
        self._filePath = ''
        self._dialog = None

        # Create self._dialog instance and call
        # necessary methods to create a user interface
        self._createUI()

        self.mediaObj = self._dialog.videoPlayer.mediaObject()
        self.audioSink = self._dialog.videoPlayer.audioOutput()

        self._dialog.seekSlider.setMediaObject(self.mediaObj)
        self._dialog.volumeSlider.setAudioOutput(self.audioSink)

        # Connect slots with signals.
        self._connect()

        # Show the Audio player.
        self.show()

    def _createUI(self):
        """
        Create self._dialog using the class Ui_VideoPlayerDialog.
        Tweak some UI elements
        """

        self._dialog = Ui_VideoPlayerDialog()
        self._dialog.setupUi(self)
        self._dialog.retranslateUi(self)
        playIcon= QIcon("play.png")
        pauseIcon= QIcon("pause.png")
        stopIcon= QIcon("stop.png")
        musicIcon= QIcon("music.png")

        self._dialog.playToolButton.setIcon(playIcon)
        self._dialog.pauseToolButton.setIcon(pauseIcon)
        self._dialog.stopToolButton.setIcon(stopIcon)
        self.setWindowIcon(musicIcon)


    def closeEvent(self, evt):
        """
        Overrides the QMainWindow.closeEvent
        """
        self._dialog.videoPlayer.stop()
        QMainWindow.closeEvent(self, evt)

    def _connect(self):
        """
        Connect slots with signals.
        """
        self.connect(self._dialog.fileOpenAction,
                     SIGNAL("triggered()"),
                     self._openFileDialog)

        self.connect(self._dialog.fileExitAction,
                     SIGNAL("triggered()"),
                     self.close)

        self.connect(self._dialog.fullScreenAction,
                     SIGNAL("toggled(bool)"),
                     self._toggleFullScreen)

        self.connect(self._dialog.playToolButton,
                     SIGNAL("clicked()"),
                     self._playMedia)

        self.connect(self._dialog.stopToolButton,
                     SIGNAL("clicked()"),
                     self._stopMedia)

        self.connect(self._dialog.pauseToolButton,
                     SIGNAL("clicked()"),
                     self._pauseMedia)

    def _toggleFullScreen(self, val):
        """
        Change between normal and full screen mode.
        """

        # Note: The program starts in Normal viewing mode
        # by default.

        if val:
            self.showFullScreen()
        else:
            self.showNormal()


    def _openFileDialog(self):
        """
        Opens the QFileDialog for accepting user input
        for the input image file path (self._filePath)
        """

        self._filePath = ''

        self._filePath = \
            str(QFileDialog.getOpenFileName(
                self,
                "Open Video File",
                "",
                "Video file (*.mpg);;AVI(*.avi);;All Files (*.*);;"))

        if self._filePath:
            self._filePath = os.path.normpath(self._filePath)
            self._dialog.fileLineEdit.setText(self._filePath)
            self._loadNewMedia()

    def _loadNewMedia(self):
        """
        Create a new MediaSource object using the specified
        file path.
        """
        #This is required so that the player can play another file.
        # if loaded.
        if self.mediaSource:
            self._stopMedia()
            del self.mediaSource
        self.mediaSource = phonon.Phonon.MediaSource(self._filePath)

    def _playMedia(self):
        """
        Play the opened media file
        """
        if not self._okToPlayPauseStop():
            return
        self._dialog.videoPlayer.play(self.mediaSource)

    def _stopMedia(self):
        """
        Stop streaming the media
        """
        if not self._okToPlayPauseStop():
            return
        self._dialog.videoPlayer.stop()

    def _pauseMedia(self):
        """
        Pause the media streaming
        """
        if not self._okToPlayPauseStop():
            return
        self._dialog.videoPlayer.pause()

    def _okToPlayPauseStop(self):
        """
        Determines if the medai source can be played paused or stopped.
        """
        okToProceed = True
        if self.mediaSource is None:
            err="Specify an audio file using File->Open"
            self._dialog.fileLineEdit.setText(err)
            okToProceed = False

        return okToProceed

#----------------------------------
# Run the Video Player !
#----------------------------------
app = QApplication(sys.argv)
videoPlayer = VideoPlayerDialog()
app.exec_()
