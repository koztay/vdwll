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
#    -  This file, CombiningAudio.py is an audio processing utility
#       created as an illustration for:
#       Chapter 6 section "Project: Combining Audio Clips"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  A utility that takes two audio files, and combines the specified
#      portions of the audio clips into a single audio file.
#    - Shows how to add fade out effect at the end of each audio clips.
#    - Illustrates how to add a silent audio track between two audio clips.
#    - Shows how to construct and link a GStreamer bin.
#    - Makes use of functionality in GStreamer plug-in, gnonlin.
#    - Among many other things, it illustrates several basic GStreamer audio
#       processing techniques. Example: message handling, setting up
#       dynamic pads, adding and linking elements in a pipeline.
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
#   Replace the values of inFileLocation_1, inFileLocation_2 in method
#   AudioMerger.addGnlFileSources with appropriate audio file paths on your
#   machine. Similarly, replace the value of self.outFileLocation with an
#   appropriate output file path.  Windows user: Be sure to specify the path
#   with forward slashes such as":
#   C:/AudioFiles/audio1.mp3 and NOT like -- C:\AudioFiles\audio1.mp3.
#
#   Then run the program in the command console as:
#
#           $python CombiningAudio.py
#
#   This should create an audio file that combines the given audio clips.

# TODO:
#   - Add a feature that can accept input such as audio files, their duration
#   and position on main timeline and so on from a text file. You will need to
#   refactor the AudioMerger.addGnlFileSources method
#   - See a detailed note about deprecation warning for
#    gst.Controller.set_interpolation_mode(), in file AudioEffects.py
#-------------------------------------------------------------------------------

import os, sys, time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst

class AudioMerger:
    """
    AudioMerger class combines two or mode audio clips putting them into
    a single audio output file. The clips are separated by a silent
    audio and fade out effect is implemented for each of the audio clip.
    """
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.is_playing = False
        self.seek_done = False
        self.position = 0
        self.duration = None

        # The following fade_* variables are set in
        # self.addGnlFileSources()
        self.fade_start_1 = 0
        self.fade_start_2 = 0
        self.fade_end_1 = 0
        self.fade_end_2 = 0

        #Flag used for printing purpose only.
        self.error_msg = ''

        self.outFileLocation = "C:/AudioFiles/combined_audio.mp3"

        self.constructPipeline()
        self.connectSignals()

    def printUsage(self):
        usage = ("\n Utility that combines multiple audio clips"
                 "\n Specify appropriate input and output paths in the "
                 "\n class AudioMerger and then run the program as \n"
                 "python CombiningAudio.py")

        return usage

    def constructPipeline(self):
        """
         Construct the Gstreamer pipeline
         @see: self.addGnlFileSources()
         @see: self.addFadingEffect()
        """
        self.pipeline = gst.Pipeline()
        self.composition = gst.element_factory_make("gnlcomposition")

        # Add audio tracks to the gnl Composition
        self.addGnlFileSources()

        self.encoder = gst.element_factory_make("lame",
                                                "mp3_encoder")
        self.filesink = gst.element_factory_make("filesink")
        self.filesink.set_property("location",
                                   self.outFileLocation)

        # Fade out the individual audio pieces
        # when that audio piece is approaching end
        self.addFadingEffect()

        self.pipeline.add(self.composition,
                          self.fadeBin,
                          self.encoder,
                          self.filesink)

        gst.element_link_many(self.fadeBin,
                              self.encoder,
                              self.filesink)

    def addFadingEffect(self):
        """
        Add the fading effect.
        @see: self.setupFadeBin()
        """
        self.setupFadeBin()

        #Volume control element
        self.volumeControl = gst.Controller(self.volume, "volume")
        self.volumeControl.set_interpolation_mode("volume",
                                                  gst.INTERPOLATE_LINEAR)

        fade_time = 20
        fade_volume = 0.5
        fade_end_time = 30

        reset_time = self.fade_end_1 + 1

        self.volumeControl.set("volume",
                               self.fade_start_1 * gst.SECOND,
                               1.0)
        self.volumeControl.set("volume",
                               self.fade_end_1 * gst.SECOND,
                               fade_volume*0.2)
        self.volumeControl.set("volume",
                               reset_time * gst.SECOND,
                               1.0)
        self.volumeControl.set("volume",
                               self.fade_start_2 * gst.SECOND,
                               1.0)
        self.volumeControl.set("volume",
                               self.fade_end_2 * gst.SECOND,
                               fade_volume*0.2)

    def setupFadeBin(self):
        """
        Creates a GStreamer bin element and adds
        elements necessary for fade out effect implementation
        Also creates and adds ghost pads.
        @see: self.addFadingEffect()
        """
        self.audioconvert = gst.element_factory_make("audioconvert")
        self.volume = gst.element_factory_make("volume")
        self.audioconvert2 = gst.element_factory_make("audioconvert")

        self.fadeBin = gst.element_factory_make("bin", "fadeBin")
        self.fadeBin.add(self.audioconvert,
                         self.volume,
                         self.audioconvert2)

        gst.element_link_many(self.audioconvert,
                               self.volume,
                               self.audioconvert2)

        #Create Ghost pads for fadeBin
        sinkPad = self.audioconvert.get_pad("sink")
        self.fadeBinSink = gst.GhostPad("sink", sinkPad)
        self.fadeBinSrc = gst.GhostPad("src", self.audioconvert2.get_pad("src"))

        self.fadeBin.add_pad(self.fadeBinSink)
        self.fadeBin.add_pad(self.fadeBinSrc)

    def addGnlFileSources(self):
        """
        Adds gnlfilesources representing the audio clips
        to be combined. Sets up these sources so that
        they properly represent the desired portion of
        the main timeline. Also creates a blank audio
        source (gnlsource). These elements are then added to
        a gnlcomposition.
        @see: self.construct_pipeline()
        """

        #Parameters for gnlfilesources
        start_time_1 = 0
        duration_1 = 20
        media_start_time_1 = 20
        media_duration_1 = 20
        inFileLocation_1 = "C:/AudioFiles/audio1.mp3"

        start_time_2 = duration_1 + 3
        duration_2 = 30
        media_start_time_2 = 20
        media_duration_2 = 30
        inFileLocation_2 = "C:/AudioFiles/audio2.mp3"

        #Parameters for blank audio between 2 tracks
        blank_start_time = 0
        blank_duration = start_time_2 + duration_2 + 3

        # These timings will be used for adding fade effects
        # See method self.addFadingEffect()
        self.fade_start_1 = duration_1 - 3
        self.fade_start_2 = start_time_2 + duration_2 - 3
        self.fade_end_1 = start_time_1 + duration_1
        self.fade_end_2 = start_time_2 + duration_2

        filesrc1 = gst.element_factory_make("gnlfilesource")
        filesrc1.set_property("uri", "file:///" + inFileLocation_1)
        filesrc1.set_property("start", start_time_1*gst.SECOND)
        filesrc1.set_property("duration", duration_1 * gst.SECOND )
        filesrc1.set_property("media-start", media_start_time_1*gst.SECOND)
        filesrc1.set_property("media-duration", media_duration_1*gst.SECOND)
        filesrc1.set_property("priority", 1)

        # Setup a gnl source that will act like a blank audio
        # source.
        gnlBlankAudio=  gst.element_factory_make("gnlsource")

        # If there are multiple audio files you can specify the
        # least priority value  instead of priority of 3.
        # The following also ensures that if blank_duration
        # has a value much greater than the overall duration
        # of the timeline, the redudndent silent portion is
        # *not* played at the end.
        gnlBlankAudio.set_property("priority", 4294967295)

        # Alternatively, you can set the priority as 3
        # since there are only 2 clips and we have properly defined
        # blank_duration.Code commented out.
        ##gnlBlankAudio.set_property("priority", 3)

        gnlBlankAudio.set_property("start",blank_start_time)
        gnlBlankAudio.set_property("duration", blank_duration * gst.SECOND)
        gnlBlankAudio.set_property("media-start",blank_start_time)
        gnlBlankAudio.set_property("media-duration", blank_duration * gst.SECOND)

        blankAudio = gst.element_factory_make("audiotestsrc")
        blankAudio.set_property("wave", 4)
        gnlBlankAudio.add(blankAudio)

        filesrc2 = gst.element_factory_make("gnlfilesource")
        filesrc2.set_property("uri", "file:///" + inFileLocation_2)
        filesrc2.set_property("start", start_time_2 * gst.SECOND)
        filesrc2.set_property("duration", duration_2 * gst.SECOND )
        filesrc2.set_property("media-start", media_start_time_2*gst.SECOND)
        filesrc2.set_property("media-duration", media_duration_2*gst.SECOND)
        filesrc2.set_property("priority", 2)

        self.composition.add(gnlBlankAudio)
        self.composition.add(filesrc1)
        self.composition.add(filesrc2)


    def gnonlin_pad_added(self, gnonlin_elem, pad):
        """
        Captures the pad-added signal emitted by
        gnlcomposition and links the dynamic pad
        with an appropriate pad on other element
        (in this case pad on self.fadeBin)
        """
        caps = pad.get_caps()
        #compatible_pad = self.audioconvert.get_compatible_pad(pad, caps)
        compatible_pad = self.fadeBin.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # capture the messages put on the bus.
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        #connect the pad_added signal for conposition.
        self.composition.connect("pad-added",
                                 self.gnonlin_pad_added)

    def run(self):
        """
        Run the audio cutter.
        """
        self.is_playing = True
        self.pipeline.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)
        self.printFinalStatus()
        evt_loop.quit()

    def printFinalStatus(self):
        if self.error_msg:
            print "\n ", self.error_msg
        else:
            print "\n Done combining audio. "
            print "\n The audio written to: ", self.outFileLocation

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
audioMerger = AudioMerger()
thread.start_new_thread(audioMerger.run, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()





