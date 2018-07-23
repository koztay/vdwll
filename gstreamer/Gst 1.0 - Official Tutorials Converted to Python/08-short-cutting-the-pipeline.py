#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Basic tutorial 8: Short-cutting the pipeline
https://gstreamer.freedesktop.org/documentation/tutorials/basic/short-cutting-the-pipeline.html
"""
import sys
import logging
import gi

gi.require_versions({'Gtk': '3.0', 'Gst': '1.0', 'GstApp': '1.0'})

from gi.repository import Gst, GLib, Gtk, GstApp
from array import array


Gst.init(None)
Gst.debug_set_colored(Gst.DebugColorMode.ON)
Gst.debug_set_active(True)
Gst.debug_set_default_threshold(4)
# Gst.debug_set_threshold_for_name('fatal_warnings', 6)
# Gst.debug_set_threshold_for_name('WARN', Gst.DebugLevel.LOG  )

CHUNK_SIZE = 1024  # Amount of bytes we are sending in each buffer
SAMPLE_RATE = 44100  # Samples per second we are sending

AUDIO_CAPS = 'audio/x-raw, rate=44100, format=S16LE, ' \
                'channels=1, layout=interleaved, ' \
                'channel-mask=0x0000000000000003'

# Structure to contain all our information, so we can pass it to callbacks
class CustomData:
    pipeline = None
    app_source = None
    tee = None
    audio_queue = None
    audio_convert1 = None
    audio_resample = None
    audio_sink = None
    video_queue = None
    audio_convert2 = None
    visual = None
    video_convert = None
    video_sink = None
    app_queue = None
    app_sink = None
    num_samples = 0
    a = 0.0
    b = 0.0
    c = 0.0
    d = 0.0
    sourceid = 0
    main_loop = None


class Main:
    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Short-cutting the pipeline")
        window.set_default_size(300, -1)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        self.button = Gtk.Button("Start")
        self.button.connect("clicked", self.start_stop)
        vbox.add(self.button)
        window.show_all()

        self.data = CustomData()
        # Initialize custom data structure
        self.data.a = 0.0
        self.data.b = 1.0
        self.data.c = 0.0
        self.data.d = 1.0

        # Create the elements
        self.data.app_source = Gst.ElementFactory.make("appsrc", "app_source")
        self.data.tee = Gst.ElementFactory.make("tee", "tee")
        self.data.audio_queue = Gst.ElementFactory.make("queue", "audio_queue")
        self.data.audio_convert1 = Gst.ElementFactory.make("audioconvert",
                                                      "audio_convert1")
        self.data.audio_resample = Gst.ElementFactory.make("audioresample",
                                                      "audio_resample")
        self.data.audio_sink = Gst.ElementFactory.make("autoaudiosink", "audio_sink")

        self.data.video_queue = Gst.ElementFactory.make("queue", "video_queue")
        self.data.audio_convert2 = Gst.ElementFactory.make("audioconvert",
                                                      "audio_convert2")
        self.data.visual = Gst.ElementFactory.make("wavescope", "visual")
        self.data.video_convert = Gst.ElementFactory.make("videoconvert", "csp")
        self.data.video_sink = Gst.ElementFactory.make("glimagesink", "video_sink")

        self.data.app_queue = Gst.ElementFactory.make("queue", "app_queue")
        self.data.app_sink = Gst.ElementFactory.make("appsink", "app_sink")

        self.data.pipeline = Gst.Pipeline.new("test-pipeline")

        if not (self.data.app_source and
                self.data.tee and
                self.data.audio_queue and
                self.data.audio_convert1 and
                self.data.audio_resample and
                self.data.audio_sink and
                self.data.video_queue and
                self.data.audio_convert2 and
                self.data.visual and
                self.data.video_convert and
                self.data.video_sink and
                self.data.app_queue and
                self.data.app_sink and
                self.data.pipeline):
            print("Not all elements could be created.", file=sys.stderr)
            sys.exit(-1)

        # Configure wavescope
        self.data.visual.set_properties({"shader": 0, "style": 0})

        # Configure appsrc
        audio_caps = Gst.caps_from_string(AUDIO_CAPS)
        self.data.app_source.set_property("caps", audio_caps)
        self.data.app_source.connect("need-data", self.start_feed, self.data)
        self.data.app_source.connect("enough-data", self.stop_feed, self.data)

        # Configure appsink
        self.data.app_sink.set_properties({"emit-signals": True, "caps": audio_caps})
        self.data.app_sink.connect("new-sample", self.new_sample, self.data)

        # Link all elements that can be automatically linked because they have "Always" pads
        [self.data.pipeline.add(k) for k in [
            self.data.app_source, self.data.tee,
            self.data.audio_queue, self.data.audio_convert1, self.data.audio_resample, self.data.audio_sink,
            self.data.video_queue, self.data.audio_convert2, self.data.visual,
            self.data.video_convert, self.data.video_sink,
            self.data.app_queue, self.data.app_sink]]

        if not (self.data.app_source.link(self.data.tee) and
                    (self.data.audio_queue.link(self.data.audio_convert1) and
                         self.data.audio_convert1.link(self.data.audio_resample) and
                         self.data.audio_resample.link(self.data.audio_sink)) and
                    (self.data.video_queue.link(self.data.audio_convert2) and
                         self.data.audio_convert2.link(self.data.visual) and
                         self.data.visual.link(self.data.video_convert) and
                         self.data.video_convert.link(self.data.video_sink)) and
                    self.data.app_queue.link(self.data.app_sink)):
            print("Elements could not be linked.", file=sys.stderr)
            sys.exit(-1)

        # print('data.audio_convert2.parse_context()', data.audio_convert2.parse_context())

        # Manually link the Tee, which has "Request" pads
        tee_audio_pad = self.data.tee.get_request_pad("src_%u")
        print("Obtained request pad {0} for audio branch".format(
            tee_audio_pad.get_name()))
        queue_audio_pad = self.data.audio_queue.get_static_pad("sink")

        tee_video_pad = self.data.tee.get_request_pad("src_%u")
        print("Obtained request pad {0} for video branch".format(
            tee_video_pad.get_name()))
        queue_video_pad = self.data.video_queue.get_static_pad("sink")

        tee_app_pad = self.data.tee.get_request_pad("src_%u")
        print("Obtained request pad {0} for app branch".format(tee_app_pad.get_name()))
        queue_app_pad = self.data.app_queue.get_static_pad("sink")

        if (tee_audio_pad.link(queue_audio_pad) != Gst.PadLinkReturn.OK or
                    tee_video_pad.link(queue_video_pad) != Gst.PadLinkReturn.OK or
                    tee_app_pad.link(queue_app_pad) != Gst.PadLinkReturn.OK):
            print("Tee could not be linked.", file=sys.stderr)
            sys.exit(-1)

        # Instruct the bus to emit signals for each received message, and connect to the interesting signals
        bus = self.data.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_message)
        # bus.connect("message::error", self.error_cb, self.data)
        # bus.connect("message::eos", self.eos_cb, self.data)

        # Start playing the pipeline
        # data.pipeline.set_state(Gst.State.PLAYING)

        # Create a GLib Mainloop and set it to run
        self.data.main_loop = GLib.MainLoop()
        self.data.main_loop.run()

        # Free resources
        # data.pipeline.set_state(Gst.State.NULL)

    def bus_message(self, bus, message):
        t = message.type

        if t == Gst.MessageType.EOS:
            self.data.pipeline.set_state(Gst.State.NULL)
            logging.info('Done')
            self.data.main_loop.quit()

        if t == Gst.MessageType.WARNING:
            self.data.pipeline.set_state(Gst.State.NULL)
            warning = message.warning()
            logging.warning('Warning: {}\n{}'.format(*warning))

        if t == Gst.MessageType.ERROR:
            self.data.pipeline.set_state(Gst.State.NULL)
            error = message.parse_error()
            logging.error('{}\n{}'.format(*error))

    def start_stop(self, w):
        if self.button.get_label() == "Start":
            self.button.set_label("Stop")
            self.data.pipeline.set_state(Gst.State.PLAYING)
        elif self.button.get_label() == "Stop":
            self.data.pipeline.set_state(Gst.State.NULL)
            self.button.set_label("Start")

    def drange(self, start, stop, step=1.0):
        r = start
        while r < stop:
            yield r
            r += step

    # This method is called by the idle GSource in the mainloop, to feed CHUNK_SIZE bytes into appsrc.
    # The idle handler is added to the mainloop when appsrc requests us to start sending data (need-data signal)
    # and is removed when appsrc has enough data (enough-data signal)
    def push_data(self, data):
        num_samples = CHUNK_SIZE / 2  # Because each sample is 16 bits

        # Generate some psychodelic waveforms
        self.data.c += self.data.d
        self.data.d -= self.data.c / 1000.0
        freq = 1100.0 + 1000.0 * self.data.d

        raw = array('H')
        # print(num_samples)
        for i in self.drange(0, num_samples):
            self.data.a += self.data.b
            self.data.b -= self.data.a / freq
            a5 = (int(500 * self.data.a)) % 65535
            raw.append(a5)
        # b_data = raw.tostring()
        b_data = raw.tostring()

        self.data.num_samples += num_samples
        buffer = Gst.Buffer.new_wrapped(b_data)

        # Set its pts (Presentation Time Stamp) and duration
        buffer.pts = Gst.util_uint64_scale(self.data.num_samples, Gst.SECOND,
                                           SAMPLE_RATE)

        buffer.duration = Gst.util_uint64_scale(CHUNK_SIZE, Gst.SECOND,
                                                SAMPLE_RATE)

        # Push the buffer into the appsrc
        ret = self.data.app_source.emit('push-buffer', buffer)
        if ret != Gst.FlowReturn.OK:
            return False
        return True

    # This signal callback triggers when appsrc needs data. Here, we add an idle handler
    # to the mainloop to start pushing data into the appsrc
    def start_feed(self, source, size, data):
        if self.data.sourceid == 0:
            print("Start feeding")
            self.data.sourceid = GLib.idle_add(self.push_data, self.data)

    # This callback triggers when appsrc has enough data and we can stop sending.
    # We remove the idle handler from the mainloop
    def stop_feed(self, source, data):
        if self.data.sourceid != 0:
            print("Stop feeding")
            GLib.source_remove(self.data.sourceid)
            self.data.sourceid = 0

    # The appsink has received a buffer
    def new_sample(self, sink, data):

        # Retrieve the buffer
        sample = sink.emit("pull-sample")
        if sample:
            # The only thing we do in this example is print a * to indicate a received buffer
            print("*")
            sample.unref()

            # This function is called when an error message is posted on the bus

    def error_cb(self, bus, msg, data):
        err, debug_info = msg.parse_error()
        print(
            "Error received from element %s: %s" % (msg.src.get_name(), err),
            file=sys.stderr)
        print("Debugging information: %s" % debug_info, file=sys.stderr)
        self.data.main_loop.quit()

    def eos_cb(self, bus, msg, data):
        self.data.main_loop.quit()

Main()
Gtk.main()
