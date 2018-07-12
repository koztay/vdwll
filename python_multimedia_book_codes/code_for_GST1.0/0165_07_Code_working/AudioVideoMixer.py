#-------------------------------------------------------------------------------
# @author: Ninad Sathaye
# @copyright: 2010, Ninad Sathaye email:ninad.consult@gmail.com.
# @license: This  program is distributed under the terms of the
#           GNU General Public License GPLv3 or any later version.
#           See http://www.gnu.org/licenses/gpl-3.0.html for more details.
# @summary:
#    -  This file, AudioVideoMixer.py is mixes audio and video streams together.
#       It is created as an illustration for:
#       Chapter 7 section "Mixing Audio and Video Tracks"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  This utility mixes/combines an audio and a video track into
#      a single video file.
#    - It illustrates how to specify two file sources (one audio and one video)
#      and then merge these two media streams into a single output file.
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
#   Replace the values of self.audioInLocation, self.videoInLocation and
#   and self.outFileLocation with appropriate audio/video
#   file paths on your machine.
#
#   Windows user: Be sure to specify the path
#   with forward slashes such as":
#   C:/VideoFiles/audioInFile.mp3 and NOT like -- C:\VideoFiles\audioInFile.mp3.
#
#   Then run the program in the command console as:
#
#           $python AudioVideoMixer.py
#
#   This should create a video file that contains the input audio
#   as well as video tracks.
#-------------------------------------------------------------------------------

import os, sys, time
import thread
import getopt, glob
import gobject
import pygst
pygst.require("0.10")
import gst


class AudioVideoMixer:
    """
    This utility mixes an audio and a video track into
    a single video file.
    """
    def __init__(self):
        self.is_playing = False
        # Flag used for printing purpose only.
        self.error_msg = ''

        self.audioInLocation = "C:/VideoFiles/audioOut.mp3"
        self.videoInLocation = "C:/VideoFiles/videoOut.mp4"
        self.outFileLocation = "C:/VideoFiles/mixed.mp4"

        self.constructPipeline()
        self.connectSignals()

    def constructPipeline(self):
        """
        Create an instance of gst.Pipeline, create, add element objects
        to this pipeline. Create appropriate connections between the elements.
        """
        self.pipeline = gst.Pipeline("pipeline")

        self.audiosrc = gst.element_factory_make("filesrc")
        self.audiosrc.set_property("location", self.audioInLocation)

        self.videosrc = gst.element_factory_make("filesrc")
        self.videosrc.set_property("location", self.videoInLocation)

        self.filesink = gst.element_factory_make("filesink")
        self.filesink.set_property("location", self.outFileLocation)

        self.decodebin_1 = gst.element_factory_make("decodebin")
        self.decodebin_2 = gst.element_factory_make("decodebin")

        self.audioconvert = gst.element_factory_make("audioconvert")
        self.audio_encoder= gst.element_factory_make("lame")

        self.video_encoder = gst.element_factory_make("ffenc_mpeg4")
        self.muxer = gst.element_factory_make("ffmux_mp4")
        self.queue = gst.element_factory_make("queue")

        # As a precaution add video capability filter
        # in the video processing pipeline.
        videocap = gst.Caps("video/x-raw-yuv")
        self.capsFilter = gst.element_factory_make("capsfilter")
        self.capsFilter.set_property("caps", videocap)
        # Converts the video from one colorspace to another
        self.colorSpace = gst.element_factory_make("ffmpegcolorspace")

        self.pipeline.add( self.videosrc,
                           self.decodebin_2,
                           self.capsFilter,
                           self.colorSpace,
                           self.video_encoder,
                           self.muxer,
                           self.filesink)

        self.pipeline.add(self.audiosrc,
                          self.decodebin_1,
                          self.audioconvert,
                          self.audio_encoder,
                          self.queue)

        # Link audio elements
        gst.element_link_many(self.audiosrc, self.decodebin_1)
        gst.element_link_many( self.audioconvert, self.audio_encoder,
                               self.queue, self.muxer)
        #Link video elements
        gst.element_link_many(self.videosrc, self.decodebin_2)
        gst.element_link_many(self.capsFilter,
                              self.colorSpace,
                              self.video_encoder,
                              self.muxer,
                              self.filesink)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # capture the messages put on the bus.
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect the decodebin_1 and decodebin_2 "pad-added" signals.
        self.decodebin_1.connect("pad-added", self.decodebin_pad_added)

        # Connect the decodebin "pad_added" signal.
        self.decodebin_2.connect("pad-added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Link decodebin pad-added signal.
        """
        compatible_pad = None
        caps = pad.get_caps()
        name = caps[0].get_name()
        print "\n cap name is = ", name
        if name[:5] == 'video' and (decodebin is self.decodebin_2):
            compatible_pad = self.capsFilter.get_compatible_pad(pad, caps)
        elif name[:5] == 'audio' and (decodebin is self.decodebin_1) :
            compatible_pad = self.audioconvert.get_compatible_pad(pad, caps)


        if compatible_pad:
            pad.link(compatible_pad)


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
            print "\n Done mixing audio and video tracks. "
            print "\n The resultant file written to: ", \
            self.outFileLocation

# Run the program
mixer = AudioVideoMixer()
thread.start_new_thread(mixer.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()
