import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject


GObject.threads_init()
Gst.init(None)


class SimplePipeLine2:
    def __init__(self):
        pipe_desc = "filesrc name=src ! oggdemux ! theoradec ! videoconvert ! ximagesink"

        self.pipeline = Gst.parse_launch(pipe_desc)
        self.filesrc = self.pipeline.get_by_name('src')


loop = GObject.MainLoop()
p = SimplePipeLine2()
p.filesrc.set_property('location', 'video.ogv')
p.pipeline.set_state(Gst.State.PLAYING)
loop.run()
