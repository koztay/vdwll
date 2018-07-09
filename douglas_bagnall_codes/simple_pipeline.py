import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject


GObject.threads_init()
Gst.init(None)


class SimplePipeLine:
    def __init__(self):
        self.pipeline = Gst.Pipeline()
        self.filesrc = Gst.ElementFactory.make('filesrc')
        self.oggdemux = Gst.ElementFactory.make('oggdemux')
        self.theoradec = Gst.ElementFactory.make('theoradec')
        self.videoconvert = Gst.ElementFactory.make('videoconvert')
        self.ximagesink = Gst.ElementFactory.make('ximagesink')

        self.pipeline.add(self.filesrc)
        self.pipeline.add(self.oggdemux)
        self.pipeline.add(self.theoradec)
        self.pipeline.add(self.videoconvert)
        self.pipeline.add(self.ximagesink)

        self.filesrc.link(self.oggdemux)
        self.oggdemux.link(self.theoradec)
        self.theoradec.link(self.videoconvert)
        self.videoconvert.link(self.ximagesink)


loop = GObject.MainLoop()
p = SimplePipeLine()
p.filesrc.set_property('location', 'video.ogv')
p.pipeline.set_state(Gst.State.PLAYING)
loop.run()
