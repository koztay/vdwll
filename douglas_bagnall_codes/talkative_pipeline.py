import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject


GObject.threads_init()
Gst.init(None)


class TalkativePipeline:
    def __init__(self):
        pipe_desc = "filesrc name=src ! oggdemux ! theoradec ! videoconvert ! ximagesink"

        self.pipeline = Gst.parse_launch(pipe_desc)
        self.filesrc = self.pipeline.get_by_name('src')

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
        # self.bus.connect('message::eos', self.on_eos)
        # self.bus.connect('message::error', self.on_error)
        # self.bus.connect('message::element', self.on_element)

    def on_message(self, bus, msg):
        s = msg.get_structure()
        print(s.get_name())
        print(s.to_string())


loop = GObject.MainLoop()
p = TalkativePipeline()
p.filesrc.set_property('location', 'video.ogv')
p.pipeline.set_state(Gst.State.PLAYING)
loop.run()
