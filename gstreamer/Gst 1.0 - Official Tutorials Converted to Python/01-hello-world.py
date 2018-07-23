
# coding=utf-8
# https://gstreamer.freedesktop.org/documentation/tutorials/basic/hello-world.html
# Also big thanks to https://stackoverflow.com/questions/35137165/gstreamer-1-0-video-from-tutorials-is-not-playing-on-macos

import gi
gi.require_versions({'Gst': '1.0'})

from gi.repository import Gst, GLib

Gst.init(None)
Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)


class Main:
    def __init__(self):
        self.pipeline = Gst.parse_launch('playbin uri=https://gstreamer.freedesktop.org/data/media/small/sintel.mkv')
        self.pipeline.set_state(Gst.State.PLAYING)
        self.main_loop = GLib.MainLoop.new(None, False)
        GLib.MainLoop.run(self.main_loop)
        self.bus = self.pipeline.get_bus()
        self.msg = self.bus.timed_pop_filtered(
            Gst.CLOCK_TIME_NONE,
            Gst.MessageType.ERROR | Gst.MessageType.EOS
        )

        if self.msg is not None:
            self.msg.unref()
        self.bus.unref()
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline.unref()

Main()

