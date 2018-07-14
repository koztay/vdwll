#!/usr/bin/env python

import cairo
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk


class TransparentWindow(Gtk.Window):
    def __init__(self):
        super(TransparentWindow, self).__init__()
        self.set_position(Gtk.WindowPosition.CENTER)
        # self.set_border_width(30)
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        if self.visual and self.screen.is_composited():
            print("yay")
            self.set_visual(self.visual)

        box = Gtk.Box()
        btn1 = Gtk.Button(label="foo")
        box.add(btn1)
        self.add(box)

        self.set_app_paintable(True)
        self.connect("draw", self.area_draw)
        self.show_all()

    def area_draw(self, widget, cr):
        cr.set_source_rgba(.0, .0, .0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)


TransparentWindow()
Gtk.main()
