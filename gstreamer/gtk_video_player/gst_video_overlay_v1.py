#!/usr/bin/env python3

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
    # src = Gst.ElementFactory.make("gltestsrc", None)
    src = Gst.ElementFactory.make("playbin", "player")
    src.set_property("uri", "file:///home/karnas-probook/Developer/media/pixar.mp4")
    src.set_state(Gst.State.PLAYING)
    sink = Gst.ElementFactory.make("ximagesink", None)

    if not sink or not src:
        print ("GL elements not available.")
        exit()

    pipeline.add(src)
    pipeline.add(sink)
    src.link(sink)

    window = Gtk.Window()
    window.connect("delete-event", window_closed, pipeline)
    window.set_default_size(1280, 720)
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
        Gtk.main()
