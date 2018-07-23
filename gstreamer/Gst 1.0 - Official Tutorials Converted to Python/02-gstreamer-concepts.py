# coding=utf-8
# https://gstreamer.freedesktop.org/documentation/tutorials/basic/concepts.html
# thanks to https://github.com/gkralik/python-gst-tutorial

"""
bunda start butonuna basmak lazım. Ancak her stop startta yeni pencerede oynatıyor...
"""

import gi
# import sys

gi.require_versions({'Gtk': '3.0', 'Gst': '1.0'})
from gi.repository import Gst, GObject, GLib, Gtk

Gst.init(None)
Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)


class Main:
    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Videotestsrc-Player")
        window.set_default_size(300, -1)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        self.button = Gtk.Button("Start")
        self.button.connect("clicked", self.start_stop)
        vbox.add(self.button)
        window.show_all()

        self.pipeline = Gst.Pipeline.new('pipeline')
        source = Gst.ElementFactory.make('videotestsrc', 'source')
        sink = Gst.ElementFactory.make('glimagesink', 'sink')

        if not self.pipeline or not source or not sink:
            print('Elements could not be linked.\n')
            self.pipeline.unref()
            # sys.exit(1)

        [self.pipeline.add(k) for k in [source, sink]]

        source.link(sink)
        if not source.link(sink):
            print("ERROR: Could not link source to sink")
            # sys.exit(1)

        source.set_property('pattern', 0)

        self.bus = self.pipeline.get_bus()

        # Don't working with that code
        # self.msg = self.bus.timed_pop_filtered(
        #     Gst.CLOCK_TIME_NONE,
        #     Gst.MessageType.ERROR | Gst.MessageType.EOS
        # )

        # if self.msg:
        #     t = self.msg.type
        #     if t == Gst.MessageType.ERROR:
        #         err, dbg = self.msg.parse_error()
        #         print("ERROR:", self.msg.src.get_name(), " ", err.message)
        #         if dbg:
        #             print("debugging info:", dbg)
        #     elif t == Gst.MessageType.EOS:
        #         print("End-Of-Stream reached")
        #     else:
        #         # this should not happen. we only asked for ERROR and EOS
        #         print("ERROR: Unexpected message received.")

    def start_stop(self, w):
        if self.button.get_label() == "Start":
            self.button.set_label("Stop")
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            self.pipeline.set_state(Gst.State.NULL)
            self.button.set_label("Start")


Main()
Gtk.main()
