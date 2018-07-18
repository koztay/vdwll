import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


class VideoPlayer:
    """
    Simple Video player that just 'plays' a valid input Video file.
    """

    def __init__(self, location, moviewindow):
        self.video_width = 1200
        self.video_height = 600
        self.crop_left = 20
        self.crop_right = 20
        self.crop_bottom = 20
        self.crop_top = 20

        self.location = location
        self.movie_window = moviewindow

        self.player = Gst.parse_launch(
            "rtspsrc location={} latency=10 ! decodebin ! autovideosink".format(self.location))
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)

        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)
            self.player.set_state(Gst.State.NULL)

    def on_sync_message(self, bus, message):
        struct = message.get_structure()
        if not struct:
            return
        message_name = struct.get_name()
        if message_name == "prepare-window-handle":
            # Assign the viewport
            self.imagesink = message.src
            self.imagesink.set_property("force-aspect-ratio", False)
            self.imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())
            self.player.set_state(Gst.State.PLAYING)
