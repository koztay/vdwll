from gi.repository import Gtk


window = Gtk.Window()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
