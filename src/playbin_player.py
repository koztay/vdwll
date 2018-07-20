import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GstVideo


class VideoPlayer:
    """
    Simple Video player that just 'plays' a valid input Video file.
    """

    def __init__(self, uri, moviewindow):
        Gst.init(None)

        self.uri = uri
        self.movie_window = moviewindow

        self.player = Gst.ElementFactory.make("playbin", "playbin")
        self.player.set_property("uri", self.uri)

        self.streams_list = []

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        # connect to interesting signals in playbin
        self.player.connect("video-tags-changed", self.on_tags_changed)
        self.player.connect("audio-tags-changed", self.on_tags_changed)
        self.player.connect("text-tags-changed", self.on_tags_changed)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)

        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
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

    # this function is called when new metadata is discovered in the stream
    def on_tags_changed(self, playbin, stream):
        # we are possibly in a GStreamer working thread, so we notify
        # the main thread of this event through a message in the bus
        self.player.post_message(
            Gst.Message.new_application(
                self.player,
                Gst.Structure.new_empty("tags-changed")))

    # extract metadata from all the streams and write it to the text widget
    # in the GUI
    def analyze_streams(self):

        # read some properties
        nr_video = self.player.get_property("n-video")
        nr_audio = self.player.get_property("n-audio")
        nr_text = self.player.get_property("n-text")

        for i in range(nr_video):
            tags = None
            # retrieve the stream's video tags
            tags = self.player.emit("get-video-tags", i)
            if tags:
                self.streams_list.append("video stream {0}\n".format(i))
                _, str = tags.get_string(Gst.TAG_VIDEO_CODEC)
                self.streams_list.append(
                    "  codec: {0}\n".format(
                        str or "unknown"))

        for i in range(nr_audio):
            tags = None
            # retrieve the stream's audio tags
            tags = self.player.emit("get-audio-tags", i)
            if tags:
                self.streams_list.append("\naudio stream {0}\n".format(i))
                ret, str = tags.get_string(Gst.TAG_AUDIO_CODEC)
                if ret:
                    self.streams_list.append(
                        "  codec: {0}\n".format(
                            str or "unknown"))

                ret, str = tags.get_string(Gst.TAG_LANGUAGE_CODE)
                if ret:
                    self.streams_list.append(
                        "  language: {0}\n".format(
                            str or "unknown"))

                ret, str = tags.get_uint(Gst.TAG_BITRATE)
                if ret:
                    self.streams_list.append(
                        "  bitrate: {0}\n".format(
                            str or "unknown"))

        for i in range(nr_text):
            tags = None
            # retrieve the stream's subtitle tags
            tags = self.player.emit("get-text-tags", i)
            if tags:
                self.streams_list.append("\nsubtitle stream {0}\n".format(i))
                ret, str = tags.get_string(Gst.TAG_LANGUAGE_CODE)
                if ret:
                    self.streams_list.append(
                        "  language: {0}\n".format(
                            str or "unknown"))

        print(self.streams_list)

    # this function is called when an "application" message is posted on the bus
    # here we retrieve the message posted by the on_tags_changed callback
    def on_application_message(self, bus, msg):
        if msg.get_structure().get_name() == "tags-changed":
            # if the message is the "tags-changed", update the stream info in
            # the GUI
            self.analyze_streams()

    def play(self):
        self.player.set_state(Gst.State.PLAYING)

    def stop(self):
        self.player.set_state(Gst.State.NULL)


if __name__ == "__main__":
    Gst.init(None)
