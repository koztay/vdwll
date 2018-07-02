import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Button Ekleme Testi")

        # add button to the window:
        self.button = Gtk.Button(label="Bana tıkla!")
        self.button.connect("clicked", self.button_clicked)
        self.add(self.button)

    def button_clicked(self, widget):
        print("bana tıklandı!!!")


window = MainWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()

