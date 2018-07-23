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
        self.convert = Gst.ElementFactory.make('audioconvert', 'convert')
        self.sink = Gst.ElementFactory.make('osxaudiosink', 'sink')

        if not (self.pipeline and self.source and self.convert and self.sink):
            print('Not all elements could be created.')

        [self.pipeline.add(k) for k in [self.source, self.convert, self.sink]]

        if not self.convert.link(self.sink):
            print('Elements could not be linked.')
            self.pipeline.unref()

        self.source.set_property(
            'uri',
            'https://gstreamer.freedesktop.org/data/media/medium/alien.mpg'
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
            self.button.set_label("Start")


Main()
Gtk.main()
