#!/usr/bin/env python3

"""
https://lubosz.wordpress.com/2014/05/27/gstreamer-overlay-opengl-sink-example-in-python-3/

gst-launch-1.0 playbin uri=foo video-sink="glcontrol ! glimagesink"

"""

from gi.repository import Gdk
from gi.repository import Gst
from gi.repository import Gtk
from gi.repository import GdkX11  # for window.get_xid()
from gi.repository import GstVideo  # for sink.set_window_handle()

import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)


def window_closed(widget, event, pipeline):
    widget.hide()
    pipeline.set_state(Gst.State.NULL)
    Gtk.main_quit()


if __name__ == "__main__":
    Gdk.init([])
    Gtk.init([])
    Gst.init([])

    pipeline = Gst.Pipeline()
    src = Gst.ElementFactory.make("playbin", "MediaPlayer")
    src.set_property("uri", "file:///home/kemal/Videos/jason_statham.mp4")
    videosink = Gst.ElementFactory.make("glcontrol", None)
    src.set_property("video-sink", videosink)
    sink = Gst.ElementFactory.make("glimagesink", None)

    if not sink or not src:
        print("GL elements not available.")
        exit()

    pipeline.add(src)
    pipeline.add(sink)

    src.link(sink)

    window = Gtk.Window()
    window.connect("delete-event", window_closed, pipeline)
    window.set_default_size(600, 400)
    window.set_title("Hello OpenGL Sink!")

    drawing_area = Gtk.DrawingArea()
    drawing_area.set_double_buffered(True)
    window.add(drawing_area)

    window.show_all()
    window.realize()

    xid = drawing_area.get_window().get_xid()
    sink.set_window_handle(xid)

    if pipeline.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
        pipeline.set_state(Gst.State.NULL)
    else:
        pipeline.set_state(Gst.State.PLAYING)
        Gtk.main()
