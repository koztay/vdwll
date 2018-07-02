#!/usr/bin/env python3

# http://docs.gstreamer.com/pages/viewpage.action?pageId=327735

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib

pipeline = None
bus = None
message = None

# initialize GStreamer
Gst.init(None)

# build the pipeline
pipeline = Gst.parse_launch(
    "playbin uri=https://thepaciellogroup.github.io/AT-browser-tests/video/ElephantsDream.mp4"
)

# start playing
pipeline.set_state(Gst.State.PLAYING)

# wait until EOS or error
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(
    Gst.CLOCK_TIME_NONE,
    Gst.MessageType.ERROR | Gst.MessageType.EOS
)

# free resources
pipeline.set_state(Gst.State.NULL)
