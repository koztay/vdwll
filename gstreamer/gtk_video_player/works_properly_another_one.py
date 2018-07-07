#!/usr/bin/env python

import gi
gi.require_version('GstVideo', '1.0')
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')

from gi.repository import GObject, Gtk, GdkX11, Gst, GstVideo, Gdk

GObject.threads_init()
Gst.init(None)


def on_realize(window):
    win_id = window.get_window().get_xid()
    player.set_window_handle(win_id)


win = Gtk.Window()
fixed = Gtk.Fixed()
fixed.set_halign(Gtk.Align.START)
fixed.set_valign(Gtk.Align.START)


win.add(fixed)
fixed.show()

videowidget = Gtk.DrawingArea()
fixed.put(videowidget, 0, 0)
videowidget.set_size_request(640, 480)
videowidget.show()


player = Gst.ElementFactory.make('playbin', 'MultimediaPlayer')

bus = player.get_bus()

# player.set_property('uri', 'file:///home/kemal/Videos/jason_statham.mp4')
player.set_property('uri', 'file:///Users/kemal/WorkSpace/Videowall\ Development/media/webos.mp4')

# win.connect('realize', on_realize)
win.realize()

win_id = win.get_window().get_xid()
player.set_window_handle(win_id)

# hide title bar
win.get_window().set_decorations(Gdk.WMDecoration.BORDER)

# show window
win.show()
player.set_state(Gst.State.PLAYING)

# moves the window
win.get_window().move(800, 800)

# set position : https://www.youtube.com/watch?v=3z3NMkqBCZ8
win.get_window().set_position(Gtk.WIN_POS_CENTER)

# resizes the window
win.get_window().resize(1280, 720)

Gtk.main()
