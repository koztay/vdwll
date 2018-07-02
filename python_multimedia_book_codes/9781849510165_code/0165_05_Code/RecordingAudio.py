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
#    -  This file, RecordingAudio.py is a basic Audio recorder utility
#       created as an illustration for Chapter 5 section "Recording"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  A simple audio recorder program that records any audio input through
#       the microphone.
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
# GStreamer plugin dshowaudiosrc must be installed to run this program.
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
# *Running the program:
#  Then run the program in the command console as:
#
#           $python RecordigAudio.py [options]
#         The [options] are:
#        --num_buffers: The number of buffers to output
#        --out_file: The location of the output file to be written
#                    This must be an MP3 audio file.
# @TODO:
#  Extend this to save in different file format.
#
#-------------------------------------------------------------------------------

import time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst
import sys, os
from optparse import OptionParser

class AudioRecorder:
    """
    Simple audio recorder that records the input audio
    and saves it as an MP3 audio file.
    (for example audio input from a microphone)
    """
    def __init__(self):

        self.is_playing = False
        self.num_buffers = -1
        self.error_message = ""

        self.processArgs()
        self.constructPipeline()
        self.connectSignals()

    def processArgs(self):
        parser = OptionParser(usage=self.printUsage())
        parser.add_option("-n", "--num_buffers",
                          dest="num_buffers",
                          default=-1,
                          type=int,
                          help="number of buffers to output")
        parser.add_option("-o", "--out_file",
                          dest="outFilePath",
                          default="",
                          help="Output MP3 File Path")

        (options, args) = parser.parse_args()

        self.num_buffers = options.num_buffers

        self.outFileLocation = os.path.normpath(options.outFilePath)


        if not self.outFileLocation:
            print " \n Exiting program. You must specify output file."
            sys.exit(2)

        dir, fil = os.path.split(self.outFileLocation)
        fil, ext = os.path.splitext(fil)

        if ext != ".mp3":
            print "\n the output file must be of mp3 file format. Exiting"
            sys.exit(2)


    def constructPipeline(self):
        # Create the pipeline instance
        self.recorder = gst.Pipeline()

        # Define pipeline elements

        self.audiosrc = gst.element_factory_make("dshowaudiosrc")

        self.audiosrc.set_property("num-buffers",
                                   self.num_buffers)

        self.audioconvert = gst.element_factory_make("audioconvert")

        self.audioresample = gst.element_factory_make("audioresample")

        self.encoder = gst.element_factory_make("lame")

        self.filesink = gst.element_factory_make("filesink")

        self.filesink.set_property("location",
                                  self.outFileLocation)

        # Add elements to the pipeline
        self.recorder.add(self.audiosrc,
                        self.audioconvert,
                        self.audioresample,
                        self.encoder,
                        self.filesink)

        # Link elements in the pipeline.
        gst.element_link_many(self.audiosrc,
                              self.audioconvert,
                              self.audioresample,
                              self.encoder,
                              self.filesink)


    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # Capture the messages put on the bus.
        bus = self.recorder.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

    def printUsage(self):
        usage = ("Audio Recorder usage:"
        "\n $python AudioRecorder.py [options]"
        "\n The [options] are: "
        "\n --num_buffers: The number of buffers to output"
        "\n --out_file: The location of the output file to be written"
        "\n        This must be an MP3 audio file")

        return usage

    def record(self):
        """
        Record the audio
        """
        self.is_playing = True
        self.recorder.set_state(gst.STATE_PLAYING)
        print "\n Recording Audio ..."
        while self.is_playing:
            time.sleep(1)
        self.printFinalStatus()
        evt_loop.quit()


    def printFinalStatus(self):
        """
        Print the final status message.
        """
        if self.error_message:
            print self.error_message
        else:
            print "\n Done recording audio. "
            print "\n The recorded audio written to: ", self.outFileLocation

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.recorder.set_state(gst.STATE_NULL)
            self.is_playing = False
            self.error_message =  message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.recorder.set_state(gst.STATE_NULL)
            self.is_playing = False



# Run the program
recorder = AudioRecorder()
thread.start_new_thread(recorder.record, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()

