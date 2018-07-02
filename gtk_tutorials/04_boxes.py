from gi.repository import Gtk


# create a box (invisible container) with widgets inside
class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Boxes are Awesome")

        # 6px between children
        self.box = Gtk.Box(spacing=6)
        self.add(self.box)

        # Create two buttons and put them in the box
        self.bacon_button = Gtk.Button(label="Bacon")
        self.bacon_button.connect("clicked", self.clicked)

        # Pack_start means just position items in box from left to right
        self.box.pack_start(self.bacon_button, True, True, 0)

        self.tuna_button = Gtk.Button(label="Tuna")
        self.tuna_button.connect("clicked", self.clicked)
        self.box.pack_start(self.tuna_button, True, True, 0)

    # def bacon_clicked(self, widget):
    #     print("You clicked Bacon")
    #
    # def tuna_clicked(self, widget):
    #     print("You clicked Tuna")

    def clicked(self, widget):
        label = widget.get_properties("label")
        print("You clicked {}".format(label[0]))


window = MainWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
