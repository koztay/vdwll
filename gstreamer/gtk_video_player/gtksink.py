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
        self._bin = Gst.ElementFactory.make('playbin', 'MultimediaPlayer')
        self._bin.set_property('uri', 'file:///home/karnas-probook/Developer/media/pixar.mp4')

    def _on_realize(self, widget):
        pipeline = Gst.Pipeline()
        factory = pipeline.get_factory()
        gtksink = factory.make('gtksink')
        pipeline.add(gtksink)
        pipeline.add(self._bin)
        self._bin.link(gtksink)
        self.pack_start(gtksink.props.widget, True, True, 0)
        gtksink.props.widget.show()
        pipeline.set_state(Gst.State.PLAYING)


window = Gtk.ApplicationWindow()

header_bar = Gtk.HeaderBar()
header_bar.set_show_close_button(True)
window.set_titlebar(header_bar)  # Place 2

widget = GstWidget('videotestsrc')
# widget = Gst.ElementFactory.make('playbin', 'MultimediaPlayer')
#
# bus = widget.get_bus()
#
# widget.set_property('uri', 'file:///home/karnas-probook/Developer/media/pixar.mp4')
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
