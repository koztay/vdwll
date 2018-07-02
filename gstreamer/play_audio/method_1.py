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
        """
        Pipeline was automatically constructed for us by the gst.parse_ launch method.
        All it required was an appropriate command string, similar to the one specified while
        running the command-line version of GStreamer. The creation and linking
        of elements was handled internally by this method.
        :return:
        """
        my_pipeline_string = "filesrc location=/home/kemal/Music/yann_tiersen.mp3 " \
                             "! decodebin ! audioconvert ! autoaudiosink"
        self.player = gst.parse_launch(my_pipeline_string)

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


# Now run the program
player = AudioPlayer()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()
