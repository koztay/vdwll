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
#    -  This file, AudioMixer.py is mixes two audio streams together.
#       It is created as an illustration for:
#       Chapter 6 section "Audio Mixing"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  A utility that takes two input audio files and interleaves them
#       into a single output file.
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

# @Note: The interleave plug-in should be available in your GStreamer
#    installation. Typically this plug-in is available in the default GStreamer
#    installation.
#
# *Running the program:
#   Replace the values of self.inFileLocation_1, self.inFileLocation_2
#   and self.outFileLocation with appropriate audio file paths on your machine.
#
#
#   Windows user: Be sure to specify the path
#   with forward slashes such as":
#   C:/AudioFiles/audio1.mp3 and NOT like -- C:\AudioFiles\audio1.mp3.
#
#   Then run the program in the command console as:
#
#           $python AudioMixer.py
#
#   This should create an audio file with the two input files merged into an
#   interleaved output audio file.
#-------------------------------------------------------------------------------

import os, sys, time
import thread
import getopt, glob
import gobject
import pygst
pygst.require("0.10")
import gst


class AudioMixer:
    def __init__(self):
        self.is_playing = False
        # Flag used for printing purpose only.
        self.error_msg = ''

        self.inFileLocation_1 = "C:/AudioFiles/audio1.mp3"
        self.inFileLocation_2= "C:/AudioFiles/audio2.mp3"
        self.outFileLocation = "C:/AudioFiles/audio_mix.mp3"

        self.constructPipeline()
        self.connectSignals()


    def constructPipeline(self):
        """
        Create a GStreamer pipeline using parse_launch()
        """
        audio1_str = (" filesrc location=%s ! "
                      "decodebin ! audioconvert  "
                      % (self.inFileLocation_1) )

        audio2_str = (" filesrc location=%s "
                      "! decodebin ! audioconvert "
                      %(self.inFileLocation_2))

        interleave_str = ("interleave name=mix ! "
                          " audioconvert ! lame ! "
                          " filesink location=%s"
                          %self.outFileLocation )

        queue_str = " ! queue ! mix."

        myPipelineString = ( interleave_str + audio1_str
                             + queue_str + audio2_str
                             + queue_str )


        self.pipeline = gst.parse_launch(myPipelineString)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # capture the messages put on the bus.
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

    def play(self):
        """
        Start streaming the audio
        """
        self.is_playing = True
        self.pipeline.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)
        self.printFinalStatus()
        evt_loop.quit()

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False
            self.error_msg =  message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False

    def printFinalStatus(self):
        """
        Print final status message.
        """
        if self.error_msg:
            print "\n ", self.error_msg
        else:
            print "\n Done mixing audio clips. "
            print "\n The audio written to: ", self.outFileLocation

# Run the program
mixer = AudioMixer()
thread.start_new_thread(mixer.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()
