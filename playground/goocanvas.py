import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '2.0')
from gi.repository import Gtk, GooCanvas


def main(args):
    w = Gtk.Window()
    w.connect('destroy', lambda x: Gtk.main_quit())

    cv = GooCanvas.Canvas()
    cv_root = cv.get_root_item()
    rect = GooCanvas.CanvasRect(
            parent=cv_root,
            stroke_color='red',
            x=10, y=20,
            width=400, height=30)

    w.add(cv)
    w.show_all()
    Gtk.main()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))