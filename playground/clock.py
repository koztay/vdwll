#!/usr/bin/python
from gi.repository import Gtk, GObject
from datetime import datetime


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="app")

        self.box = Gtk.Box(spacing=6)
        self.add(self.box)

        self.label = Gtk.Label()
        self.box.pack_start(self.label, True, True, 0)

    # Displays Timer
    def displayclock(self):
        #  putting our datetime into a var and setting our label to the result.
        #  we need to return "True" to ensure the timer continues to run, otherwise it will only run once.
        datetimenow = str(datetime.now())
        self.label.set_label(datetimenow)
        return True

    # Initialize Timer
    def startclocktimer(self):
        #  this takes 2 args: (how often to update in millisec, the method to run)
        GObject.timeout_add(1000, self.displayclock)


win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
win.startclocktimer()
Gtk.main()
