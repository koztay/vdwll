#!/usr/bin/env python3


from gi.repository import Gtk


class Demo:

    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title('Demo')
        self.window.set_default_size(300, 300)
        self.window.set_border_width(5)
        self.window.connect('delete-event', self.on_app_exit)

        hbox = Gtk.Box()
        hbox.set_halign(Gtk.Align.CENTER)
        hbox.set_valign(Gtk.Align.CENTER)
        self.window.add(hbox)

        da = Gtk.DrawingArea()
        da.set_size_request(100, 100)
        hbox.pack_start(da, False, False, 5)

        button = Gtk.Button('Show')
        button.connect('clicked', self.on_button_clicked, da)
        hbox.pack_start(button, False, False, 5)

        self.second_win = Gtk.Window()
        self.second_win.set_title('flying window')
        # You may also want to remove window decoration.
        #self.second_win.set_decorated(False)

        label = Gtk.Label('second window')
        self.second_win.add(label)


    def run(self):
        self.window.show_all()
        Gtk.main()

    def on_app_exit(self, widget, event=None):
        Gtk.main_quit()

    def on_button_clicked(self, button, da):
        allocation = da.get_allocation()
        self.second_win.set_default_size(allocation.width,
                allocation.height)
        pos = self.window.get_position()
        self.second_win.move(pos[0] + allocation.x, pos[1] + allocation.y)
        self.second_win.show_all()


if __name__ == '__main__':
    demo = Demo()
    demo.run()