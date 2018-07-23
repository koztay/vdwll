#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Basic tutorial 12: Streaming
https://gstreamer.freedesktop.org/documentation/tutorials/basic/streaming.html
"""

import gi
import sys
import logging

gi.require_version('Gst', '1.0')

from gi.repository import Gst, GLib


class CustomData:
    is_live = None
    pipeline = None
    main_loop = None


class Main:
    def __init__(self):

        Gst.init(None)
        Gst.debug_set_active(True)
        Gst.debug_set_default_threshold(2)

        self.data = CustomData()

        self.data.pipeline = Gst.parse_launch('playbin uri=https://www.freedesktop.org/software/gstreamer-sdk/data/media/sintel_trailer-480p.webm')
        bus = self.data.pipeline.get_bus()

        ret = self.data.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print('ERROR: Unable to set the pipeline to the playing state.')
            sys.exit(-1)
        elif ret == Gst.StateChangeReturn.NO_PREROLL:
            self.data.is_live = True

        self.data.main_loop = GLib.MainLoop.new(None, False)

        bus.add_signal_watch()
        bus.connect('message', self.cb_message, self.data)

        self.data.main_loop.run()

    def cb_message(self, bus, msg, data):
        t = msg.type

        if t == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            logging.error('{}\n{}'.format(*err))
            self.data.pipeline.set_state(Gst.State.READY)
            self.data.main_loop.quit()
            return

        if t == Gst.MessageType.EOS:
            # end-of-stream
            self.data.pipeline.set_state(Gst.State.READY)
            self.data.main_loop.quit()
            return

        if t == Gst.MessageType.BUFFERING:
            persent = 0

            # If the stream is live, we do not care about buffering.
            if self.data.is_live:
                return

            persent = msg.parse_buffering()
            print('Buffering {0}%'.format(persent))

            if persent < 100:
                self.data.pipeline.set_state(Gst.State.PAUSED)
            else:
                self.data.pipeline.set_state(Gst.State.PLAYING)
            return

        if t == Gst.MessageType.CLOCK_LOST:
            self.data.pipeline.set_state(Gst.State.PAUSED)
            self.data.pipeline.set_state(Gst.State.PLAYING)
            return

Main()
