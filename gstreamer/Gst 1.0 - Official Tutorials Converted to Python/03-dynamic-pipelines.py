#!/usr/bin/env python3
# coding=utf-8
# https://gstreamer.freedesktop.org/documentation/tutorials/basic/dynamic-pipelines.html

"""
bunda ses var video yok...
"""

import gi

gi.require_versions({'Gtk': '3.0', 'Gst': '1.0'})
from gi.repository import Gst, Gtk

Gst.init(None)
Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)


class Main:
    def __init__(self):
        self.video_width = 1200
        self.video_height = 600
        self.crop_left = 20
        self.crop_right = 20
        self.crop_bottom = 20
        self.crop_top = 20

        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Dynamic Hello World")
        window.set_default_size(300, -1)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        self.button = Gtk.Button("Start")
        self.button.connect("clicked", self.start_stop)
        vbox.add(self.button)
        window.show_all()

        self.pipeline = Gst.Pipeline.new('test-pipeline')

        self.source = Gst.ElementFactory.make('uridecodebin', 'source')
        # self.convert = Gst.ElementFactory.make('audioconvert', 'convert')
        # self.sink = Gst.ElementFactory.make('osxaudiosink', 'sink')
        self.convert = Gst.ElementFactory.make('videoconvert', 'convert')

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

        # # Converts the video from one colorspace to another
        # self.colorspace = Gst.ElementFactory.make("videoconvert")
        #
        # self.videobox = Gst.ElementFactory.make("videobox")
        # self.videobox.set_property("bottom", self.crop_bottom)
        # self.videobox.set_property("top", self.crop_top)
        # self.videobox.set_property("left", self.crop_left)
        # self.videobox.set_property("right", self.crop_right)

        # self.player.add(self.autoconvert)
        # self.player.add(self.videobox)
        # self.player.add(self.capsfilter)
        # self.player.add(self.colorspace)
        # self.player.add(self.videosink)

        # self.queue1.link(self.autoconvert)
        # self.autoconvert.link(self.videobox)
        # self.videobox.link(self.capsfilter)
        # self.capsfilter.link(self.colorspace)
        # self.colorspace.link(self.videosink)

        self.sink = Gst.ElementFactory.make('autovideosink', 'sink')

        if not (self.pipeline
                and self.source
                and self.convert
                and self.capsFilter
                # and self.colorspace
                # and self.videobox
                and self.sink):
            print('Not all elements could be created.')

        [self.pipeline.add(k) for k in [self.source,
                                        self.convert,
                                        self.capsFilter,
                                        # self.colorspace,
                                        # self.videobox,
                                        self.sink]]

        if not self.convert.link(self.capsFilter):
            print('capsfilter element could not be linked.')
            self.pipeline.unref()
        if not self.capsFilter.link(self.sink):
            print('capsfilter element could not be linked.')
            self.pipeline.unref()

        # if not self.capsfilter.link(self.colorspace):
        #     print('colorspace element could not be linked.')
        #     self.pipeline.unref()
        # if not self.colorspace.link(self.videobox):
        #     print('videobox element could not be linked.')
        #     self.pipeline.unref()
        # if not self.videobox.link(self.sink):
        #     print('videobox element could not be linked.')
        #     self.pipeline.unref()

        self.source.set_property(
            'uri',
            # 'rtsp://10.0.0.143/media/video1'
            'file:///Users/kemal/WorkSpace/Videowall Development/media/pixar.mp4'
        )

        self.source.connect('pad-added', self.on_pad_added)

    def on_pad_added(self, src, new_pad):
        sink_pad = self.convert.get_static_pad('sink')
        print(
            "Received new pad '%s' from '%s'" %
            (new_pad.get_name(), src.get_name())
        )
        if sink_pad.is_linked():
            print("We are already linked. Ignoring.")
            return

        new_pad_caps = new_pad.get_current_caps()
        new_pad_struct = new_pad_caps.get_structure(0)
        new_pad_type = new_pad_struct.get_name()

        if not new_pad_type.startswith('audio/x-raw'):
            print(
                "It has type '%s' which is not raw audio. Ignoring."
                % new_pad_type
            )

        ret = new_pad.link(sink_pad)
        if not ret == Gst.PadLinkReturn.OK:
            print("Type is '%s' but link failed" % new_pad_type)
        else:
            print("Link succeeded (type '%s')" % new_pad_type)
        return

    def start_stop(self, w):
        if self.button.get_label() == "Start":
            self.button.set_label("Stop")
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            self.pipeline.set_state(Gst.State.NULL)
            # self.pipeline.set_state(Gst.State.PAUSED)
            # paused yapınca olmuyor, NULL ve PLAYING yapacaksın. "we were already PLAYING" diyor...
            # self.source.set_property(
            #     'uri',
            #     'https://www.freedesktop.org/software/gstreamer-sdk/data/media/sintel_trailer-480p.webm'
            # )
            # self.pipeline.set_state(Gst.State.PLAYING)
            self.button.set_label("Start")


Main()
Gtk.main()
