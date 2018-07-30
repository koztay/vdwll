"""
https://developer.gnome.org/ClutterGstGirPython/
"""


from gi.repository import GObject
from gi.repository import Clutter
from gi.repository import ClutterGst
from gi.repository import Gst


class Video(object):
    def __init__(self, filename):
        self.stage = Clutter.Stage()
        self.stage.set_fullscreen(True)
        # self.stage.set_size(1000, 600)
        self.stage.set_color(Clutter.Color.new(0x11, 0x11, 0x11, 0xff))
        self.stage.set_title('GStreamer Clutter Python - ' + filename)
        self.stage.connect('key-press-event', self.on_key_press_event)
        self.stage.connect('destroy', self.on_destroy)
        self.texture = Clutter.Texture.new()
        self.texture.connect('size-change', self.on_size_change)
        self.stage.add_actor(self.texture)
        self.sink = ClutterGst.VideoSink.new(self.texture)
        self.sink.set_property('sync', True)
        self.player = Gst.ElementFactory.make('playbin', None)
        self.player.set_property('video-sink', self.sink)
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)
        self.bus.connect('message::error', self.on_error)
        self.stage.show_all()
        self.player.set_property('uri', 'file://' + filename)
        self.player.set_state(Gst.State.PLAYING)

    def on_size_change(self, texture, width, height):
        print('on_size_change:')
        stage = texture.get_stage()
        if stage is not None:
            dx, dy = stage.get_size()
            texture.set_anchor_point(width / 2, height / 2)
            texture.set_position(dx / 2, dy / 2)

    def on_error(self, bus, msg):
        print('on_error:', msg.parse_error())

    def on_eos(self, bus, msg):
        print('on_eos:', msg)
        self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)
        self.player.set_state(Gst.State.PAUSED)

    def on_destroy(self, stage, event):
        print('on_destroy:', event)
        self.player.set_state(Gst.State.NULL)
        Clutter.main_quit()

    def on_key_press_event(self, stage, event):
        print('on_key_press_event', event)
        if event.unicode_value:
            c = event.unicode_value
            if c in 'qx':
                self.on_destroy(stage, event)
                print('quit')
            elif c in 'pP':
                self.player.set_state(Gst.State.PAUSED)
                print('pause')
            elif c in 'gG':
                self.player.set_state(Gst.State.PLAYING)
                print('play')
            elif c in 'sS':
                self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)
                self.player.set_state(Gst.State.PAUSED)
                print('stop')


if __name__ == '__main__':
    from sys import argv

    GObject.threads_init()
    Gst.init(argv)
    ClutterGst.init(argv)
    Clutter.init(argv)
    video = Video(*argv[1:])
    Clutter.main()
