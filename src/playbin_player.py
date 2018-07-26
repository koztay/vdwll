import gi
import logging
import sys

gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import GObject, Gst, GstVideo


class CustomData:
    is_live = None
    pipeline = None
    # main_loop = None  # belki bunu application 'da set ederiz.


class VideoPlayer:
    """
    Simple Video player that just 'plays' a valid input Video file.
    """

    def __init__(self, uri, moviewindow):
        Gst.init(None)
        Gst.debug_set_active(True)
        Gst.debug_set_default_threshold(2)

        self.data = CustomData()

        self.uri = uri
        self.movie_window = moviewindow

        self.data.pipeline = Gst.ElementFactory.make("playbin", "playbin")
        self.data.pipeline.set_property("uri", self.uri)

        # rtspsrc kullanırsan aşağıdaki gibi :
        # self.data.pipeline = Gst.parse_launch(
        #     "rtspsrc location={} latency=500 ! decodebin ! autovideosink".format(self.uri))

        self.streams_list = []

        bus = self.data.pipeline.get_bus()

        ret = self.data.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print('ERROR: Unable to set the pipeline to the playing state.')
            sys.exit(-1)
        elif ret == Gst.StateChangeReturn.NO_PREROLL:
            self.data.is_live = True

        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('message', self.cb_message, self.data)
        bus.connect("sync-message::element", self.on_sync_message)

    def cb_message(self, bus, msg, data):
        gst_state = self.data.pipeline.get_state(Gst.CLOCK_TIME_NONE)
        # print("STATE cb_message begin:", gst_state.state.value_name, gst_state.state.value_nick)
        if gst_state.state.value_name == "GST_STATE_PLAYING":
            print("I am playing")

        while gst_state.state.value_name != "GST_STATE_PLAYING":
            self.data.pipeline.set_state(Gst.State.PLAYING)

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
            self.data.pipeline.set_state(Gst.State.PAUSED)
            self.data.pipeline.set_state(Gst.State.PLAYING)

            return

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


if __name__ == "__main__":
    Gst.init(None)
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(2)
