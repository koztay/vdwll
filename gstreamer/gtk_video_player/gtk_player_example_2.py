from pprint import pprint

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gtk, Gst
Gst.init(None)
Gst.init_check(None)


class GstWidget(Gtk.Box):
    def __init__(self, pipeline):
        super().__init__()
        self.connect('realize', self._on_realize)
        # self._bin = Gst.parse_bin_from_description('videotestsrc', True)


    def _on_realize(self, widget):
        pipeline = Gst.Pipeline()
        factory = pipeline.get_factory()
        gtksink = factory.make('gtksink')
        # gtksink = Gst.ElementFactory.make('gtksink', 'gtksink')
        pipeline.add(gtksink)
        self.player = Gst.ElementFactory.make('playbin', 'player')
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        print("player ney amk :", self.player)
        self.player.set_property("video-sink", fakesink)


        self.uri = "file:///home/kemal/Videos/jason_statham.mp4"

        pipeline.add(self.player)
        self.player.link(gtksink)
        self.pack_start(gtksink.props.widget, True, True, 0)
        gtksink.props.widget.show()
        self.player.set_property("uri", self.uri)
        pipeline.set_state(Gst.State.PLAYING)


window = Gtk.ApplicationWindow()

header_bar = Gtk.HeaderBar()
header_bar.set_show_close_button(True)
window.set_titlebar(header_bar)  # Place 2

widget = GstWidget('videotestsrc')
widget.set_size_request(200, 200)

window.add(widget)

window.show_all()

def on_destroy(win):
    try:
        Gtk.main_quit()
    except KeyboardInterrupt:
        pass

window.connect('destroy', on_destroy)

Gtk.main()
