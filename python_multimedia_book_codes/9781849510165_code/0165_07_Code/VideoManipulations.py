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
#    -  This file, VideoManipulations.py is a command line utility that
#       illustrates basic video manipulations such as cropping and resizing
#       created as an illustration for Chapter 7 section:
#       "Video Manipulations and Effects"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  A simple Video player utility that illustrates basic video
#       manipulations such as cropping and resizing
#    - The program also illustrates how to setup video processing pipeline
#       that enables resizing or cropping the video.
#      It uses plug-ins such as videobox, ffmpegcolorspace, capsfilter,
#      autovideosink to accomplish this task.
#
# Dependencies
#---------------
#  In order to run the program the following packages need to be installed and
#  appropriate environment variables need to be set (if it is not done by the
#  installer automatically.)
# 1. Python 2.6
# 2. GStreamer 0.10.5 or later version
# 3. Python bindings for GStreamer v 0.10.15 or later
# 4. PyGObject v 2.14 or later
# 5. The following is a partial list of GStreamer plug-ins
#   that should be available in your GStreamer installation. Typically
#   these plugi-ins are available by default. If not, install those.
#   ffmpegcolorspace, autoconvert, capsfilter,
#   autovideosink, autoaudiosink
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
#
#
# *Running the program:
#   Replace self.inFileLocation, C:/VideoFiles/my_music.mp4
#   with a valid Video file path. Then run the program in the
#   command console as:
#
#  $python VideoManipulations.py
#
#-------------------------------------------------------------------------------

import time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst
import os
from optparse import OptionParser

class VideoPlayer:
    """
    Simple Video player that just 'plays' a valid input Video file.
    """
    def __init__(self):
        self.use_parse_launch = False
        self.decodebin = None

        self.video_width = 800
        self.video_height= 600
        self.crop_left   = 20
        self.crop_right  = 20
        self.crop_bottom = 20
        self.crop_top    = 20

        self.inFileLocation="C:/VideoFiles/my_music.mp4"

        self.constructPipeline()
        self.is_playing = False
        self.connectSignals()

    def constructPipeline(self):
        """
        Add and link elements in a GStreamer pipeline.
        """
        # Create the pipeline instance
        self.player = gst.Pipeline()

        # Define pipeline elements
        self.filesrc = gst.element_factory_make("filesrc")
        self.filesrc.set_property("location",
                                  self.inFileLocation)
        self.decodebin = gst.element_factory_make("decodebin")

        # Add elements to the pipeline
        self.player.add(self.filesrc, self.decodebin)

        # Link elements in the pipeline.
        gst.element_link_many(self.filesrc, self.decodebin)

        self.constructAudioPipeline()
        self.constructVideoPipeline()



    def constructAudioPipeline(self):
        """
        Define and link elements to build the audio portion
        of the main pipeline.
        @see: self.construct_pipeline()
        """
         # audioconvert for audio processing pipeline
        self.audioconvert = gst.element_factory_make("audioconvert")
        self.queue2 = gst.element_factory_make("queue")
        self.audiosink = gst.element_factory_make("autoaudiosink")

        self.player.add(self.queue2,
                        self.audioconvert,
                        self.audiosink)

        gst.element_link_many(self.queue2,
                              self.audioconvert,
                              self.audiosink)


    def constructVideoPipeline(self):
        """
        Define and links elements to build the video portion
        of the main pipeline.
        @see: self.construct_pipeline()
        """
        # Autoconvert element for video processing
        self.autoconvert = gst.element_factory_make("autoconvert")
        self.videosink = gst.element_factory_make("autovideosink")

        # Set the capsfilter
        if self.video_width and self.video_height:
            videocap = gst.Caps("video/x-raw-yuv," \
            "width=%d, height=%d"%(self.video_width,
                                self.video_height))
        else:
            videocap = gst.Caps("video/x-raw-yuv")

        self.capsFilter = gst.element_factory_make("capsfilter")
        self.capsFilter.set_property("caps", videocap)

        # Converts the video from one colorspace to another
        self.colorSpace = gst.element_factory_make("ffmpegcolorspace")

        self.queue1 = gst.element_factory_make("queue")

        self.videobox = gst.element_factory_make("videobox")
        self.videobox.set_property("bottom", self.crop_bottom )
        self.videobox.set_property("top", self.crop_top )
        self.videobox.set_property("left", self.crop_left )
        self.videobox.set_property("right", self.crop_right )

        self.player.add(self.queue1,
                        self.autoconvert,
                        self.videobox,
                        self.capsFilter,
                        self.colorSpace,
                        self.videosink)

        gst.element_link_many(self.queue1,
                              self.autoconvert,
                              self.videobox,
                              self.capsFilter,
                              self.colorSpace,
                              self.videosink)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # Capture the messages put on the bus.
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect the decodebin signal
        if not self.decodebin is None:
            self.decodebin.connect("pad_added",
                                   self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        queue elements, when the decodebin "pad-added" signal
        is generated.
        """
        compatible_pad = None
        caps = pad.get_caps()
        name = caps[0].get_name()
        print "\n cap name is = ", name
        if name[:5] == 'video':
            compatible_pad = self.queue1.get_compatible_pad(pad, caps)
        elif name[:5] == 'audio':
            compatible_pad = self.queue2.get_compatible_pad(pad, caps)

        if compatible_pad:
            pad.link(compatible_pad)

    def play(self):
        """
        Play the media file
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
            print "\n Unable to play Video. Error: ", \
            message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False

# Run the program
player = VideoPlayer()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()






