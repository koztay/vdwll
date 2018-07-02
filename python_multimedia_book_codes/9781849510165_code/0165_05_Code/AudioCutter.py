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
#    -  This file, AudioCutter.py is a simple Audio cutting utility
#       created as an illustration for Chapter 5 section ,
#        'Extracting Part of an Audio' of the book:
#       "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
# This utility creates a new MP3 audio file by cutting out
# a specified portion of an input MP3 audio file. The original file
# remains UNCHANGED.
# The important parameters are hard coded in the  __init__ method of
# class AudioCutter in this file. These parameters are:
#
#  self.media_start_time:  The position in the input media file, which will
#                become the start position of the extracted media.
#                This is specified in seconds BUT, later converted into
#                nanoseconds while setting up necessary properties.
#  self.media_duration: Total duration of the extracted media file
#                     ( beginning from  media-start).
#  self.inFileLocation: Full path of the input audio file.
#  self.outFileLocation: Full path of the output audio file
#
# *Running the program:

#   Specify appropriate values for the above parameters and then run the
#     program on command line as:
#
#           $python AudioCutter.py
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
# Your GStreamer installation must have gnonlin plugin installed. Run:
#    $gst-inspect-0.10  gnonlin
# in a shell window to check if this plugin is installed. ( Windows users
# should run gst-inspect-0.10.exe gnonlin from command prompt)
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
# @TODO:
#      1. Modify this program so that the parameters such as media_start_time
#         can be passed as an argument to the program.
#      2. Add support for other file formats. For example, extend this code so
#         that it can extract a piece from a wav file and save it as an MP3
#         audio file.
#
#-------------------------------------------------------------------------------

import os, sys, time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst

class AudioCutter:
    """
    A utility that creates a new mp3 audio file
    by extracting the specified portion of an input
    mp3 audio file
    """

    def __init__(self):
        self.is_playing = False
        # Flag used for printing purpose only.
        self.error_msg = ''

        self.media_start_time = 170
        self.media_duration = 15
        self.inFileLocation = "C:\AudioFiles\my_music.mp3"
        self.outFileLocation = "C:\AudioFiles\my_music_chunk.mp3"

        self.constructPipeline()
        self.connectSignals()

    def constructPipeline(self):
        self.pipeline = gst.Pipeline()
        self.filesrc = gst.element_factory_make("gnlfilesource")

        # Set properties of filesrc element
        # Note: the gnlfilesource signal will be connected
        # in self.connectSignals()
        self.filesrc.set_property("uri",
                                  "file:///" + self.inFileLocation)
        self.filesrc.set_property("media-start",
                                  self.media_start_time*gst.SECOND)
        self.filesrc.set_property("media-duration",
                                  self.media_duration*gst.SECOND)

        self.audioconvert = gst.element_factory_make("audioconvert")

        self.encoder = gst.element_factory_make("lame", "mp3_encoder")

        self.filesink = gst.element_factory_make("filesink")

        self.filesink.set_property("location",
                                   self.outFileLocation)

        #Add elements to the pipeline
        self.pipeline.add(self.filesrc, self.audioconvert,
                          self.encoder, self.filesink)
        # Link elements
        gst.element_link_many(self.audioconvert,self.encoder,
                              self.filesink)



    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # capture the messages put on the bus.
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        #gnlsource plugin uses dynamic pads.
        # Capture the pad_added signal.
        self.filesrc.connect("pad-added",
                             self.gnonlin_pad_added)

    def gnonlin_pad_added(self, gnonlin_elem, pad):
        """
        Capture the pad_added signal to manually
        link gnlfilesrc pad with the audioconvert.
        """
        caps = pad.get_caps()
        compatible_pad = self.audioconvert.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

    def run(self):
        """
        Run the audio cutter.
        """
        self.is_playing = True
        print "\n Converting audio. Please be patient.."
        self.pipeline.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)
        self.printFinalStatus()
        evt_loop.quit()

    def printFinalStatus(self):
        """
        Print final status message.
        """
        if self.error_msg:
            print "\n ", self.error_msg
        else:
            print "\n Done extracting audio. "
            print "\n The extracted audio written to: ", self.outFileLocation

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False
            self.error_msg = message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False

#Run the program
audioCutter = AudioCutter()
thread.start_new_thread(audioCutter.run, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()
