#!/usr/bin/env python

import sys, os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gtk
# from gi.repository import GObject, Gst, GstVideo

from video_player import VideoPlayer

class GTK_Main:
    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Realtime RTSP Player")
        window.set_default_size(500, 400)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        self.movie_window = Gtk.DrawingArea()
        vbox.add(self.movie_window)
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        hbox.set_border_width(10)
        hbox.pack_start(Gtk.Label(), False, False, 0)
        self.button = Gtk.Button("Start")
        self.button.connect("clicked", self.start_stop)
        hbox.pack_start(self.button, False, False, 0)
        self.button2 = Gtk.Button("Quit")
        self.button2.connect("clicked", self.exit)
        hbox.pack_start(self.button2, False, False, 0)
        hbox.add(Gtk.Label())
        window.show_all()

        # Set up the gstreamer pipeline
        # self.player = Gst.parse_launch("rtspsrc location=rtsp://10.0.0.143/media/video1 latency=10 ! decodebin ! autovideosink")
        # bus = self.player.get_bus()
        # bus.add_signal_watch()
        # bus.enable_sync_message_emission()
        # bus.connect("message", self.on_message)
        # bus.connect("sync-message::element", self.on_sync_message)
        self.player = VideoPlayer(location="rtsp://10.0.0.143/media/video1", moviewindow=window)

    def start_stop(self, w):
        if self.button.get_label() == "Start":
            self.button.set_label("Stop")
            self.player.play()
        else:
            self.player.stop()
            self.button.set_label("Start")

    def exit(self, widget, data=None):
        Gtk.main_quit()
"""
    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")

    def on_sync_message(self, bus, message):
        struct = message.get_structure()
        if not struct:
            return
        message_name = struct.get_name()
        if message_name == "prepare-window-handle":
            # Assign the viewport
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())
"""
# Gst.init(None)
GTK_Main()
GObject.threads_init()
Gtk.main()
