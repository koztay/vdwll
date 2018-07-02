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
#    -  This file, MusicVisualizer.py is a audio player/ visualizer utility.
#       created as an illustration for:
#       Chapter 6 section "Visualizing an Audio Track"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  A utility that takes an input audio file and plays it along with
#       the audio visualization effects.
#---------------
# Dependencies
#---------------
#  In order to run the program the following packages need to be installed and
#  appropriate environment variables need to be set (if it is not done by the
#  installer automatically.)
# 1. Python 2.6
# 2. GStreamer 0.10.5 or later version
# 3. Python bindings for GStreamer v 0.10.15 or later
# 4. PyGObject v 2.14 or later
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.

# @Note: The playbin and monoscope plug-ins must be available in your GStreamer
#    installation. Typically this plug-in is available in the default GStreamer
#    installation.
#    If monoscope viusualization plug-in is not available, try using plugins
#    like 'goom' or 'libvisual' (if available).
#
# *Running the program:
#   Replace the value of inFileLocation in __init__ method,
#   with appropriate audio file paths on your machine.
#
#   Windows user: Be sure to specify the path
#   with forward slashes such as":
#   C:/AudioFiles/audio1.mp3 and NOT like -- C:\AudioFiles\audio1.mp3.
#
#   Then run the program in the command console as:
#
#           $python MusicVisualizer.py
#
#    This should start playing the input audio file and at the same time,
#    it should also pop-up a small  window where you ca 'visualize' the
#    streaming audio.
#-------------------------------------------------------------------------------


import time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst
import os

class AudioPlayer:
    """
    Audio Player and audio visualizer utility.
    """
    def __init__(self):
        self.is_playing = False

        inFileLocation = "C:/AudioFiles/audio1.mp3"
        #Create a playbin element
        self.player = gst.element_factory_make("playbin")

        # Create the audio visualization element.
        self.monoscope = gst.element_factory_make("monoscope")
        self.player.set_property("uri", "file:///" + inFileLocation)
        self.player.set_property("vis-plugin", self.monoscope)
        # Alternative visualization plugin. Code disabled.
#        self.synaesthesia = gst.element_factory_make("synaesthesia")
#        self.player.set_property("vis-plugin", self.synaesthesia)
        self.connectSignals()

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # In this case, we only capture the messages
        # put on the bus.
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

    def play(self):
        """
        Play the music
        """
        self.is_playing = True
        self.player.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)
        evt_loop.quit()

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False
            print "\n Unable to play audio. Error: ", message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False

# Run the program
player = AudioPlayer()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()