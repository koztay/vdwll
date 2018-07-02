import thread
import time
import gobject
import pygst
pygst.require("0.10")
import gst


class AudioPlayer:
    def __init__(self):
        self.construct_pipeline()
        self.is_playing = False
        self.connect_signals()

    def construct_pipeline(self):
        self.player = gst.Pipeline()
        self.filesrc = gst.element_factory_make("filesrc")
        self.filesrc.set_property("location",
                                  "/home/kemal/Music/yann_tiersen.mp3")
        self.decodebin = gst.element_factory_make("decodebin", "decodebin")

        # Connect decodebin signal with a method
        # You can move this call to self.connect_signals
        self.decodebin.connect("pad_added", self.decodebin_pad_added)
        self.audioconvert = gst.element_factory_make("audioconvert", "audioconvert")
        self.audiosink = gst.element_factory_make("autoaudiosink", "a_a_sink")

        # Construct the pipeline
        self.player.add(self.filesrc, self.decodebin, self.audioconvert, self.audiosink)

        # Link elements in the pipeline.
        gst.element_link_many(self.filesrc, self.decodebin)
        gst.element_link_many(self.audioconvert, self.audiosink)

    def connect_signals(self):
        # In this case, we only capture the messages and put on the bus.
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

    def play(self):
        self.is_playing = True
        self.player.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)
        evt_loop.quit()

    def message_handler(self, bus, message):
        # Capture the messages on the bus a
        # set the appropriate flag.
        msg_type = message.type
        if msg_type == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False
            print("\n Unable to play audio. Error: ", message.parse_error())
        elif msg_type == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False

    def decodebin_pad_added(self, decodebin, pad):
        caps = pad.get_caps()  # caps means capabilities
        compatible_pad = self.audioconvert.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)


# Now run the program
player = AudioPlayer()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()

# gst-launch-0.10 filesrc location=/home/kemal/Music/yann_tiersen.mp3 ! decodebin ! audioconvert ! autoaudiosink
