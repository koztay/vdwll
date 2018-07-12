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
#    -  This file, PlayingVideo.py is a command line Video Player utility
#       created as an illustration for Chapter 7 section "Playing a Video"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  A simple Video player program that "plays"
#       the given Video file. It must be a valid Video format, recognizable
#       by decodebin plugin.
#    - This example covers several fundamental concepts of using
#      Gstreamer Python bindings for basic Video processing. Especially:
#    - It shows how to use queue element to process the audio and video data
#      in a pipeline.
#    - The program also illustrates how to setup video processing pipeline
#      It uses plugins such as ffmpegcolorspace, capsfilter, autovideosink to
#      accomplish this task.
#
# Dependencies
#---------------
#  In order to run the program the following packages need to be installed and
#  appropriate environment variables need to be set (if it is not done by the
#  installer automatically.)
# 1. Python 2.6
# 2. Gstreamer 0.10.5 or later version
# 3. Python bindings for Gstreamer v 0.10.15 or later
# 4. PyGObject v 2.14 or later
# 5. The following is a partial list of Gstreamer plug-ins
#   that should be available in your Gstreamer installation. Typically
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
#  $python PlayingVideo.py
#
#-------------------------------------------------------------------------------


import threading
import time
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GdkX11, GstVideo


class VideoPlayer:
    """
    Simple Video player that just 'plays' a valid input Video file.
    """
    def __init__(self):

        self.use_parse_launch = False
        self.decodebin = None
        self.inFileLocation = "/home/karnas-probook/Developer/media/pixar.mp4"

        self.construct_pipeline()
        self.is_playing = False
        self.connectSignals()

    def construct_pipeline(self):
        """
        Add and link elements in a Gstreamer pipeline.
        """
        # Create the pipeline instance

        self.player = Gst.Pipeline()

        # Define pipeline elements
        self.filesrc = Gst.ElementFactory.make("filesrc", "filesrc")
        self.filesrc.set_property("location", self.inFileLocation)

        self.decodebin = Gst.ElementFactory.make("decodebin", "decodebin")

        # audioconvert for audio processing pipeline
        self.audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")

        # Autoconvert element for video processing
        self.autoconvert = Gst.ElementFactory.make("autoconvert", "autoconvert")

        self.audiosink = Gst.ElementFactory.make("autoaudiosink", "autoaudiosink")
        self.videosink = Gst.ElementFactory.make("autovideosink", "autovideosink")

        # As a precaution add videio capability filter
        # in the video processing pipeline.

        videocap = Gst.Caps.from_string("video/x-raw")
        self.filter = Gst.ElementFactory.make("capsfilter", "filter")
        self.filter.set_property("caps", videocap)

        # Converts the video from one colorspace to another
        self.colorSpace = Gst.ElementFactory.make("ffmpegcolorspace")  # bu patlıyordu...

        self.queue1 = Gst.ElementFactory.make("queue")
        self.queue2 = Gst.ElementFactory.make("queue")

        factory = self.player.get_factory()
        self.gtksink = factory.make('gtksink')


        # print(
        #       self.filesrc,
        #       self.decodebin,
        #       self.autoconvert,
        #       self.audioconvert,
        #       self.queue1,
        #       self.queue2,
        #       self.filter,
        #       self.colorSpace,
        #       self.audiosink,
        #       self.videosink)

        # Add elements to the pipeline
        self.player.add(self.filesrc)
        self.player.add(self.decodebin)
        self.player.add(self.autoconvert)
        self.player.add(self.audioconvert)
        self.player.add(self.queue1)
        self.player.add(self.queue2)
        self.player.add(self.filter)
        self.player.add(self.audiosink)
        self.player.add(self.videosink)
        self.player.add( self.gtksink)

        # Link elements in the pipeline.
        self.filesrc.link(self.decodebin)

        self.queue1.link(self.autoconvert)
        self.autoconvert.link(self.filter)
        self.filter.link(self.gtksink)

        self.queue2.link(self.audioconvert)
        self.audioconvert.link(self.audiosink)

        """
        gst.element_link_many(self.filesrc, self.decodebin)
        gst.element_link_many(self.queue1, self.autoconvert,
                              self.filter, self.colorSpace,
                              self.videosink)
        gst.element_link_many(self.queue2, self.audioconvert,
                              self.audiosink)
        """

    def construct_pipeline_2(self):

        self.player = Gst.Pipeline.new("player")
        self.filesrc = Gst.ElementFactory.make("filesrc", "filesrc")
        self.filesrc.set_property("location", self.inFileLocation)
        self.decodebin = Gst.ElementFactory.make("decodebin", "decodebin")
        self.audioconvert = Gst.ElementFactory.make("audioconvert", "converter")
        self.videoconvert = Gst.ElementFactory.make("autoconvert", "autoconvert")
        self.audiosink = Gst.ElementFactory.make("autoaudiosink", "audio-output")
        self.videosink = Gst.ElementFactory.make("autovideosink", "video-output")
        self.queue2 = Gst.ElementFactory.make("queue", "queuea")
        self.queue1 = Gst.ElementFactory.make("queue", "queuev")
        colorspace = Gst.ElementFactory.make("videoconvert", "colorspace")

        self.player.add(self.filesrc)
        self.player.add(self.decodebin)
        self.player.add(self.audioconvert)
        self.player.add(self.audiosink)
        self.player.add(self.videosink)
        self.player.add(self.queue2)
        self.player.add(self.queue1)
        self.player.add(colorspace)

        self.filesrc.link(self.decodebin)

        self.queue1.link(self.videoconvert)
        self.queue1.link(self.gtksink)

        self.queue2.link(self.audioconvert)
        self.audioconvert.link(self.audiosink)


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
            self.decodebin.connect("pad_added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        queue elements, when the decodebin "pad-added" signal
        is generated.
        """
        compatible_pad = None
        caps = pad.query_caps(None)
        print("caps neden patlıyor? :", caps)
        name = caps.get_name()
        print("\n cap name is = ", name)
        if name[:5] == 'video':
            compatible_pad = self.queue1.get_compatible_pad(pad, caps)
            print("video pad bulundu compatible pad bulmuş mu? :", compatible_pad)

        elif name[:5] == 'audio':
            compatible_pad = self.queue2.get_compatible_pad(pad, caps)
            print("audio pad bulundu compatible pad bulmuş mu? :", compatible_pad)

        if compatible_pad:
            pad.link(compatible_pad)

    def play(self):
        """
        Play the media file
        """
        self.is_playing = True
        self.player.set_state(Gst.State.PLAYING)
        while self.is_playing:
            time.sleep(1)
        evt_loop.quit()

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            self.is_playing = False
            print("\n Unable to play Video. Error: ", message.parse_error())
        elif msgType == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.is_playing = False


# Run the program

Gst.init(None)
player = VideoPlayer()
thread = threading.Thread(target=player.play)
thread.start()
GObject.threads_init()
evt_loop = GObject.MainLoop()
evt_loop.run()






