#!/usr/bin/env python

import sys, os
import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst, GObject, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo


class GTK_Main(object):

    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Video-Player")
        window.set_default_size(500, 400)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        self.entry = Gtk.Entry()
        hbox.add(self.entry)
        self.button = Gtk.Button("Start")
        hbox.pack_start(self.button, False, False, 0)
        self.button.connect("clicked", self.start_stop)
        self.movie_window = Gtk.DrawingArea()
        vbox.add(self.movie_window)
        window.show_all()

        """
        bin = Gst.Bin.new("my-bin")
        timeoverlay = Gst.ElementFactory.make("timeoverlay")
        bin.add(timeoverlay)
        pad = timeoverlay.get_static_pad("video_sink")
        ghostpad = Gst.GhostPad.new("sink", pad)
        bin.add_pad(ghostpad)
        videosink = Gst.ElementFactory.make("autovideosink")
        bin.add(videosink)
        timeoverlay.link(videosink)
        self.player.set_property("video-sink", bin)
        """

        self.player = Gst.ElementFactory.make("playbin", "player")

        """"""
        # my_bin = Gst.Bin.new("my-bin")
        # timeoverlay = Gst.ElementFactory.make("timeoverlay")
        # my_bin.add(timeoverlay)
        # pad = timeoverlay.get_static_pad("video_sink")
        # ghostpad = Gst.GhostPad.new("sink", pad)
        # my_bin.add_pad(ghostpad)
        # videosink = Gst.ElementFactory.make("autovideosink")
        # my_bin.add(videosink)
        # timeoverlay.link(videosink)
        # self.player.set_property("video-sink", my_bin)
        # yukarıdaki kodu ekleyince de birsey olmuyor
        """"""
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

    def start_stop(self, w):
        if self.button.get_label() == "Start":
            filepath = self.entry.get_text().strip()
            if os.path.isfile(filepath):
                filepath = os.path.realpath(filepath)
                self.button.set_label("Stop")
                self.player.set_property("uri", "file://" + filepath)
                self.player.set_state(Gst.State.PLAYING)
            else:
                self.player.set_state(Gst.State.NULL)
                self.button.set_label("Start")

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.button.set_label("Start")

    def on_sync_message(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", False)
            imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())


GObject.threads_init()
Gst.init(None)
GTK_Main()
Gtk.main()
