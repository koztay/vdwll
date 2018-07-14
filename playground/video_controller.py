#!/usr/bin/env python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# videomixer-controller.py
# (c) 2008 Stefan Kost <ensonic@users.sf.net>
# Test case for the GstController using videomixer and videotestsrc

# import pygst
# pygst.require('0.10')
# import gst
import time

import gi
gi.require_version('GstVideo', '1.0')
gi.require_version('Gst', '1.0')
# gi.require_version('Gtk', '3.0')
from gi.repository import Gst


def main():
    pipeline = Gst.Pipeline("videocontroller")
    src = Gst.ElementFactory.make("videotestsrc", "src")
    mix = Gst.ElementFactory.make("videomixer", "mix")
    conv = Gst.ElementFactory.make("videoconvert", "conv")
    sink = Gst.ElementFactory.make("autovideosink", "sink")
    pipeline.add(src)
    pipeline.add(mix)
    pipeline.add(conv)
    pipeline.add(sink)

    spad = src.get_static_pad('src')
    dpad = mix.get_request_pad('sink_%d')

    spad.link(dpad)
    mix.link(conv)
    conv.link(sink)

    control = Gst.Controller(dpad, "xpos", "ypos")
    control.set_interpolation_mode("xpos", Gst.INTERPOLATE_LINEAR)
    control.set_interpolation_mode("ypos", Gst.INTERPOLATE_LINEAR)

    control.set("xpos", 0, 0)
    control.set("xpos", 5 * Gst.SECOND, 200)

    control.set("ypos", 0, 0)
    control.set("ypos", 5 * Gst.SECOND, 200)

    pipeline.set_state(Gst.STATE_PLAYING)

    time.sleep(7)


if __name__ == "__main__":
    Gst.init(None)
    main()

