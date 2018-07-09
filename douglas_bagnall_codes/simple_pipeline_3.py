import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject


GObject.threads_init()
Gst.init(None)


class SimplePipeLine3:

    def make_add_link(self, el, link=None, name=None):
        x = Gst.ElementFactory.make(el, name)
        self.pipeline.add(x)
        if link is not None:
            x.link(link)
        return x

    def __init__(self):
        self.pipeline = Gst.Pipeline()
        # sondan başa geliyoruz sanırım
        sink = self.make_add_link('xvimagesink')
        videoconvert = self.make_add_link('videoconvert', sink)
        theoradec = self.make_add_link('theoradec', videoconvert)
        oggdemux = self.make_add_link('oggdemux', theoradec)
        self.filesrc = self.make_add_link('filesrc', oggdemux, 'src')
        self.filesrc.set_property('location', 'video.ogv')

        Gst.debug_bin_to_dot_file(self.pipeline, Gst.DebugGraphDetails.ALL, 'pipeline.dot')


loop = GObject.MainLoop()
p = SimplePipeLine3()
p.filesrc.set_property('location', 'video.ogv')
p.pipeline.set_state(Gst.State.PLAYING)
loop.run()
