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
#    -  This file, AudioCutter_Method2.py is another method to extract an
#       a piece of audio clip from an audio file (the first method is discussed
#       in chapter 'Working with Audios')
#
#       This file is created as an illustration for:
#       Chapter 6 section "Project Extract Audio Using Playback Controls"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    - This utility creates a new MP3 audio file by cutting out
#      a specified portion of an input MP3 audio file. The original file
#      remains UNCHANGED.
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
#
# *Running the program:
#
#   Windows user: Be sure to specify the path
#   with forward slashes such as":
#   C:/AudioFiles/audio1.mp3 and NOT like -- C:\AudioFiles\audio1.mp3.
#
#   Then run the program in the command console as:
#
#           $python AudioCutter_Method2.py [options]
#
#   Where, the [options] are:
#   --input_file   : The path to input audio file (MP3 format) from which a
#                    piece of audio needs to be cut.
#   --output_file  : The output file path where the extracted audio will be
#                    saved. This needs to be in MP3 format.
#   --start_time   : The position in seconds on the original track. This will
#                    be the starting position of the audio to be extracted.
#   --end_time     : The position in seconds on the original track.
#                    This will be the end position of the extracted audio.
#   --verbose_mode : Prints useful information such as current position of the
#                    track (in seconds) while extracting the audio. By default,
#                    this flag is set to False.
#
#-------------------------------------------------------------------------------

import os, sys, time
import thread
import gobject
from optparse import OptionParser

import pygst
pygst.require("0.10")
import gst

class AudioCutter:
    """
    A utility that extracts an a piece of audio
    clip from an audio file.
    """
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.is_playing = False
        self.seek_done = False
        self.position = 0
        self.duration = None
        #Flag used for printing purpose only.
        self.error_msg = ''
        self.verbose_mode = False

        self.processArgs()
        self.constructPipeline()
        self.connectSignals()

    def processArgs(self):
        """
        Process the command line arguments.
        """
        parser = OptionParser(usage=self.printUsage())
        parser.add_option("-s", "--start_time",
                          dest="start_time",
                          default=0,
                          type=int,
                          help="Start time in seconds")
        parser.add_option("-e", "--end_time",
                          dest="end_time",
                          default=None,
                          help="End time in seconds")
        parser.add_option("-i", "--input_file",
                          dest="inFilePath",
                          default="",
                          help="Input File Path")
        parser.add_option("-o", "--output_file",
                          dest="outFilePath",
                          default="",
                          help="Output File Path")
        parser.add_option("-v", "--verbose_mode",
                          dest="verbose_mode",
                          action="store_true",
                          default=False,
                          help="print audio cutting progress")

        (options, args) = parser.parse_args()

        self.start_time = options.start_time
        self.start_time = self.start_time
        self.end_time = options.end_time
        self.verbose_mode = options.verbose_mode


        self.inFileLocation = os.path.normpath(options.inFilePath)
        self.outFileLocation = os.path.normpath(options.outFilePath)

        if not self.inFileLocation or not self.outFileLocation:
            print (" \n Exiting program. You must specify both,"
            " input and output files.")
            sys.exit(2)


        if not self.end_time is None:
            self.end_time = int(self.end_time)
            print "\n end_time=", self.end_time
            print "\n start_time=", self.start_time
            if self.end_time <= self.start_time:
                print ("\n WARNING: end time >= start time! "
                " Resetting the end time to end of stream")
                self.end_time = None

    def printUsage(self):
        usage = ""
        return usage

    def constructPipeline(self):
        """
        Build the GStreamer pipeline, add and link various
        GStreamer elements.
        """
        self.pipeline = gst.Pipeline()
        self.fakesink = gst.element_factory_make("fakesink")
        filesrc = gst.element_factory_make("filesrc")

        filesrc.set_property("location", self.inFileLocation)

        autoaudiosink = gst.element_factory_make("autoaudiosink")

        self.decodebin = gst.element_factory_make("decodebin")

        self.audioconvert = gst.element_factory_make("audioconvert")

        self.encoder = gst.element_factory_make("lame",
                                                "mp3_encoder")

        self.filesink = gst.element_factory_make("filesink")
        self.filesink.set_property("location", self.outFileLocation)

        self.pipeline.add(filesrc, self.decodebin, self.audioconvert,
                        self.encoder, self.fakesink)

        gst.element_link_many(filesrc, self.decodebin)
        gst.element_link_many(self.audioconvert,
                              self.encoder, self.fakesink)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        audioconvert, when the decodebin element generated "pad_added" signal
        """
        caps = pad.get_caps()
        compatible_pad = self.audioconvert.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # capture the messages put on the bus.
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect decodebin_pad_added method.
        self.decodebin.connect("pad-added", self.decodebin_pad_added)

    def run(self):
        """
        Run the audio cutter.
        """
        self.is_playing = True
        print "\n Converting audio. Please be patient.."
        self.pipeline.set_state(gst.STATE_PLAYING)
        time.sleep(1)
        while self.is_playing:
            self.extractAudio()
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

    def extractAudio(self):
        """
        Extract a piece of audio from the input audio.
        @see: self.run() which calls this method.
        """
        if not self.seek_done:
            time.sleep(0.1)
            self.duration = ( self.pipeline.query_duration(gst.FORMAT_TIME,
                                                           None) [0] )
            self.duration = self.duration/gst.SECOND

            if self.start_time > self.duration:
                print ("\n start time specified"
                " is more than the total audio duration"
                " resetting the start time to 0 sec")
                self.start_time = 0.0

            self.pipeline.seek_simple(gst.FORMAT_TIME,
                                    gst.SEEK_FLAG_FLUSH,
                                    self.start_time*gst.SECOND)

            self.pipeline.set_state(gst.STATE_PAUSED)
            self.seek_done = True
            self.pipeline.remove(self.fakesink)

            self.pipeline.add(self.filesink)
            gst.element_link_many(self.encoder, self.filesink)
            self.pipeline.set_state(gst.STATE_PLAYING)

        time.sleep(0.1)
        try:
            self.position = self.pipeline.query_position(gst.FORMAT_TIME, None)[0]
            self.position = self.position/gst.SECOND
        except gst.QueryError:
            # The pipeline has probably reached
            # the end of the audio, (and thus has 'reset' itself.)
            if self.duration is None:
                self.error_msg = ("\n Error cutting the audio file."
                " Unable to determine the audio duration.")
                self.pipeline.set_state(gst.STATE_NULL)
                self.is_playing = False
            if ( self.position <= self.duration and
                 self.position > (self.duration - 10) ):
                # Position close to the end of file.
                # Do nothing to avoid a possible traceback.
                #The audio cutting should work
                pass
            else:
                self.error_msg = " Error cutting the audio file"
                self.pipeline.set_state(gst.STATE_NULL)
                self.is_playing = False

        if not self.end_time is None:
            if self.position >= self.end_time:
                self.pipeline.set_state(gst.STATE_NULL)
                self.is_playing = False

        if self.verbose_mode:
            print "\n Current play time: =", self.position

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

# Run the program.
audioCutter = AudioCutter()
thread.start_new_thread(audioCutter.run, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()





