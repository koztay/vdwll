import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Button Ekleme Testi")

        self.label = Gtk.Label()
        self.label.set_label("Hadi ordan laaan dwdfe")
        self.label.set_angle(30)
        self.add(self.label)

        angle_property = self.label.get_properties("angle")
        print("Label angle is :", angle_property)


window = MainWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
