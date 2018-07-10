import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject


GObject.threads_init()
Gst.init(None)


class UselessPipeline:
    def make_add_link(self, el, link=None, name=None):
        x = Gst.ElementFactory.make(el, name)
        self.pipeline.add(x)
        if link is not None:
            x.link(link)
        return x

    def __init__(self, n_channels):
        self.pipeline = Gst.Pipeline()
        self.sink = self.make_add_link('autoaudiosink', None)  # auto yapınca da çalmıyor
        # self.sink = self.make_add_link('fakesink', None)
        self.sources = []
        self.interleave = self.make_add_link('interleave', self.sink)

        for i in range(n_channels):
            capsfilter = self.make_add_link('capsfilter', self.interleave)
            capsfilter.set_property("caps", Gst.caps_from_string("audio/x-raw, rate=16000, channels=1"))
            converter = self.make_add_link('audioconvert', capsfilter)
            resampler = self.make_add_link('audioresample', converter)
            parser = self.make_add_link('wavparse', resampler)
            source = self.make_add_link('filesrc', parser)
            source.set_property(
                'location',
                'truth.mp3')
            # bu olsa da olmasa da fark etmiyor
            self.sources.append(source)


loop = GObject.MainLoop()
p = UselessPipeline(n_channels=2)
p.pipeline.set_state(Gst.State.PLAYING)
loop.run()
