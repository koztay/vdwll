#!/usr/bin/python

# importing Gdk fixes the crash in gnome shell, but not gnome classic
from gi.repository import Gdk

from gi.repository import ClutterGst
from gi.repository import Clutter
from gi.repository import GtkClutter
from gi.repository import Gst
from gi.repository import Gtk

# only ClutterGst needs to be initialized to run the example correctly
#Gdk.init([])
#Gtk.init([])
#GtkClutter.init([])
#Gst.init([])
#Clutter.init([])
ClutterGst.init([])

# changing "x" to "" fixes the crash
label = Gtk.Label("x")

window = Gtk.Window()
vbox = Gtk.VBox()
window.add(vbox)

texture = Clutter.Texture.new()
sink = Gst.ElementFactory.make("cluttersink", "clutter")
sink.props.texture = texture
src = Gst.ElementFactory.make("videotestsrc", None)
pipeline = Gst.Pipeline()
pipeline.add(src)
pipeline.add(sink)
src.link(sink)

embed = GtkClutter.Embed()
embed.set_size_request(320, 240)

stage = embed.get_stage()
stage.add_child(texture)
stage.set_size(320, 240)
stage.show_all()

vbox.pack_start(embed, True, True, 0)
vbox.pack_start(label, False, False, 0)

window.connect("delete-event", Gtk.main_quit)

window.show_all()

pipeline.set_state(Gst.State.PLAYING)
Gtk.main()
