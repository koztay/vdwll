import datetime
import gi
import logging
import sys

gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import GObject, Gst, GstVideo

logging.basicConfig(filename='network_lost.log', level=logging.DEBUG)


class CustomData:
    is_live = None
    pipeline = None
    # main_loop = None  # belki bunu application 'da set ederiz.


class VideoPlayer:
    """
    Simple Video player that just 'plays' a valid input Video file.
    """

    def __init__(self,
                 uri,
                 moviewindow):

        Gst.init(None)
        Gst.debug_set_active(True)
        Gst.debug_set_default_threshold(2)

        self.data = CustomData()

        self.uri = uri
        self.movie_window = moviewindow

        self.data.pipeline = Gst.ElementFactory.make("playbin", "playbin")
        self.data.pipeline.set_property("uri", self.uri)

        self.construct_mod_queue()

        # rtspsrc kullanırsan aşağıdaki gibi :
        # self.data.pipeline = Gst.parse_launch(
        #     "rtspsrc location={} latency=500 timeout=18446744073709551 tcp-timeout=18446744073709551 ! decodebin ! autovideosink".format(self.uri))

        self.streams_list = []

        bus = self.data.pipeline.get_bus()

        ret = self.data.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print('ERROR: Unable to set the pipeline to the playing state.')
            sys.exit(-1)
        elif ret == Gst.StateChangeReturn.NO_PREROLL:
            print("Buffer oluşturmayacağız data live data...")
            self.data.is_live = True

        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('message', self.cb_message, self.data)
        bus.connect("sync-message::element", self.on_sync_message)
        # self.data.pipeline.connect('video-changed', self.on_handoff)

    def construct_mod_queue(self,
                            video_width=1920,
                            video_height=1080,
                            crop_left=0,
                            crop_right=0,
                            crop_bottom=0,
                            crop_top=0
                            ):

        ####################################################################
        # aşağıdaki kod ile bin içerisine time overlay ekledik.
        self.bin = Gst.Bin.new("my-bin")
        self.queue = Gst.ElementFactory.make("queue")
        self.bin.add(self.queue)
        queue_pad = self.queue.get_static_pad("sink")
        queue_ghostpad = Gst.GhostPad.new("sink", queue_pad)
        self.bin.add_pad(queue_ghostpad)

        # Add Videoscale Filter for Resizing
        self.videoscale = Gst.ElementFactory.make("videoscale")
        self.videoscale.set_property("method", 1)
        self.bin.add(self.videoscale)

        # Add Caps Filter for Resizing the Video
        self.caps = Gst.Caps.from_string("video/x-raw, width={}, height={}".format(
            video_width, video_height
        ))
        self.filter = Gst.ElementFactory.make("capsfilter", "filter")
        self.filter.set_property("caps", self.caps)
        self.bin.add(self.filter)

        # Add Videobox for Cropping
        self.videobox = Gst.ElementFactory.make("videobox")
        self.videobox.set_property("bottom", crop_bottom)
        self.videobox.set_property("top", crop_top)
        self.videobox.set_property("left", crop_left)
        self.videobox.set_property("right", crop_right)
        self.bin.add(self.videobox)

        # Add conversion for outputting
        self.conv = Gst.ElementFactory.make("videoconvert", "conv")
        self.bin.add(self.conv)

        # Add timeoverlay for debugging (if no debud no timeoverlay)
        self.timeoverlay = Gst.ElementFactory.make("timeoverlay")
        self.timeoverlay.set_property("text", "GNUTV")
        self.timeoverlay.set_property("font-desc", "normal 24")
        self.bin.add(self.timeoverlay)

        # Add videosink element
        self.videosink = Gst.ElementFactory.make("autovideosink")
        self.bin.add(self.videosink)

        # Link all elements
        self.queue.link(self.videoscale)
        self.videoscale.link(self.filter)
        self.filter.link(self.videobox)
        self.videobox.link(self.conv)
        self.conv.link(self.timeoverlay)
        self.timeoverlay.link(self.videosink)

        # Set videosink for pipeline
        self.data.pipeline.set_property("video-sink", self.bin)
        ####################################################################

    def cb_message(self, bus, msg, data):

        gst_state = self.data.pipeline.get_state(Gst.CLOCK_TIME_NONE)

        # logging.debug("{} state : {}".format(datetime.datetime.now(), gst_state.state.value_name))

        # if gst_state.state.value_name == "GST_STATE_PLAYING":
        #     print("I am playing")

        t = msg.type

        if t == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            try:
                logging.error('{}\n{}'.format(*err))
            except:
                print('{}'.format(err))
            self.data.pipeline.set_state(Gst.State.READY)
            # self.data.main_loop.quit()
            return

        if t == Gst.MessageType.EOS:
            # end-of-stream
            self.data.pipeline.set_state(Gst.State.READY)
            # self.data.main_loop.quit()
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

            logging.debug("{} message : Gst.MessageType.CLOCK_LOST".format(datetime.datetime.now()))
            if gst_state.state.value_name != "GST_STATE_PLAYING":
                self.data.pipeline.set_state(Gst.State.PAUSED)
                logging.debug("{} message : set paused".format(datetime.datetime.now()))
            else:
                self.data.pipeline.set_state(Gst.State.PLAYING)
                logging.debug("{} message : set playing".format(datetime.datetime.now()))

            return

        # while gst_state.state.value_name != "GST_STATE_PLAYING":
        #     # print("I am not playing, trying to set playing")
        #     self.data.pipeline.set_state(Gst.State.PLAYING)  # bu yine olmadı

    def on_sync_message(self, bus, message):
        struct = message.get_structure()
        if not struct:
            return
        message_name = struct.get_name()
        if message_name == "prepare-window-handle":
            # Assign the viewport
            self.imagesink = message.src
            print("self.imagesink neymiş", self.imagesink)
            self.imagesink.set_property("force-aspect-ratio", False)
            self.imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())

    def on_handoff(self, bus, message):
        print("Handoff oldu ya la!!")


if __name__ == "__main__":
    Gst.init(None)
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(2)
