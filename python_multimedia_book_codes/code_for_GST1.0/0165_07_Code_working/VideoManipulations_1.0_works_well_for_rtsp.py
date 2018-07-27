#!/usr/local/bin/python
# coding: utf-8
# -------------------------------------------------------------------------------

"""
Bu dosya UBUNTU DELL 'de çalışıyor. "brbad.mp4" sorunsuz oynatılıyor...
!!!!!!!!!!!!!!!!!!!   Mac 'te Çalışmıyor... !!!!!!!!!!!!!!!!!!!!!!!!!!!
"""


import time
import threading
import os
from optparse import OptionParser

import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst, GObject, Gtk


class VideoPlayer:
    """
    Simple Video player that just 'plays' a valid input Video file.
    """

    def __init__(self):
        self.use_parse_launch = False
        self.decodebin = None

        self.video_width = 5000
        self.video_height = 3000
        self.crop_left = 2500
        self.crop_right = 20
        self.crop_bottom = 1500
        self.crop_top = 20

        # self.inFileLocation = "../../../media/webos.mp4"
        self.inFileLocation = "/home/kemal/Developer/vdwll/media/brbad.mp4"
        # "/../../../media/pixar.mp4"

        self.uri = "https://www.freedesktop.org/software/gstreamer-sdk/data/media/sintel_trailer-480p.webm"

        self.constructPipeline()
        self.is_playing = False
        self.connectSignals()

    def constructPipeline(self):
        """
        Add and link elements in a GStreamer pipeline.
        """
        # Create the pipeline instance
        self.player = Gst.Pipeline()

        # Define pipeline elements
        # self.filesrc = Gst.ElementFactory.make("filesrc")
        # self.filesrc.set_property("location", self.inFileLocation)

        self.uridecodebin = Gst.ElementFactory.make("uridecodebin")
        self.uridecodebin.set_property("uri", self.uri)
        # self.decodebin = Gst.ElementFactory.make("decodebin")

        # Add elements to the pipeline
        self.player.add(self.uridecodebin)
        # self.player.add(self.decodebin)

        # Link elements in the pipeline.
        # self.uridecodebin.link(self.decodebin)

        self.constructAudioPipeline()
        self.constructVideoPipeline()

    def constructAudioPipeline(self):
        """
        Define and link elements to build the audio portion
        of the main pipeline.
        @see: self.construct_pipeline()
        """
        # audioconvert for audio processing pipeline
        self.audioconvert = Gst.ElementFactory.make("audioconvert")
        self.queue2 = Gst.ElementFactory.make("queue")
        self.audiosink = Gst.ElementFactory.make("autoaudiosink")

        self.player.add(self.queue2)
        self.player.add(self.audioconvert)
        self.player.add(self.audiosink)

        self.queue2.link(self.audioconvert)
        self.audioconvert.link(self.audiosink)

    def constructVideoPipeline(self):
        """
        Define and links elements to build the video portion
        of the main pipeline.
        @see: self.construct_pipeline()
        """
        # Autoconvert element for video processing
        self.autoconvert = Gst.ElementFactory.make("videoconvert", "convert")
        print("self.autoconvert", self.autoconvert)
        self.videosink = Gst.ElementFactory.make("autovideosink")



        # Set the capsfilter
        if self.video_width and self.video_height:
            # videocap = Gst.Caps("video/x-raw-yuv," \
            # "width=%d, height=%d"%(self.video_width,
            #                     self.video_height))
            videocap = Gst.Caps.from_string("video/x-raw, width={}, height={}".format(
                self.video_width, self.video_height))

        else:
            videocap = Gst.Caps.from_string("video/x-raw-yuv")

        self.capsFilter = Gst.ElementFactory.make("capsfilter")
        self.capsFilter.set_property("caps", videocap)

        self.videoscale = Gst.ElementFactory.make("videoscale")
        self.videoscale.set_property("method", 1)

        # Converts the video from one colorspace to another
        self.colorSpace = Gst.ElementFactory.make("videoconvert")

        self.queue1 = Gst.ElementFactory.make("queue")

        self.videobox = Gst.ElementFactory.make("videobox")
        self.videobox.set_property("bottom", self.crop_bottom)
        self.videobox.set_property("top", self.crop_top)
        self.videobox.set_property("left", self.crop_left)
        self.videobox.set_property("right", self.crop_right)

        self.player.add(self.queue1)
        self.player.add(self.autoconvert)
        self.player.add(self.videobox)
        self.player.add(self.videoscale)
        self.player.add(self.capsFilter)
        self.player.add(self.colorSpace)
        self.player.add(self.videosink)

        """
        # aşağısı çalışıyor
        self.queue1.link(self.autoconvert)
        self.autoconvert.link(self.videobox)
        self.videobox.link(self.videoscale)
        self.videoscale.link(self.capsFilter)
        self.capsFilter.link(self.colorSpace)
        self.colorSpace.link(self.videosink)
        """

        self.queue1.link(self.autoconvert)
        self.autoconvert.link(self.videoscale)
        self.videoscale.link(self.capsFilter)
        self.capsFilter.link(self.videobox)
        self.videobox.link(self.colorSpace)
        self.colorSpace.link(self.videosink)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """


        # Capture the messages put on the bus.
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect the decodebin signal
        if not self.uridecodebin is None:
            self.uridecodebin.connect("pad_added",
                                   self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        queue elements, when the decodebin "pad-added" signal
        is generated.
        """
        print("decodebin pad added layyynn")

        compatible_pad = None
        caps = pad.query_caps()
        print("caps ney ki?", caps)
        for i in range(caps.get_size()):
            structure = caps.get_structure(i)
            name = structure.get_name()
            print("{0:s}".format(name))
            # print("\n cap name is = ", name)
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
Gst.debug_set_colored(Gst.DebugColorMode.ON)
Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)
player = VideoPlayer()
thread = threading.Thread(target=player.play)
thread.start()
GObject.threads_init()
evt_loop = GObject.MainLoop()
evt_loop.run()

# GObject.threads_init()
# Gst.init(None)
# Gtk.main()  # bu satır olmalı mı acaba?
