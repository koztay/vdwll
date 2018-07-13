import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys


class MainWindow(Gtk.ApplicationWindow):
    # bunun addwidget vb. bir metodu olması lazım task olarak tabii...

    def __init__(self, app):
        Gtk.Window.__init__(self, title="GtkFixed", application=app)

        # Set the window size
        self.set_size_request(1440, 200)  # bunu settings vb. bir yerden almalı.
        # self.overlay = Gtk.Overlay()
        # self.add(self.overlay)
        # self.background = Gtk.Image.new_from_file('/Users/kemal/WorkSpace/Videowall Development/media/tvlogo_full.png')
        # self.overlay.add(self.background)

        # Add GtkFixed to the main window
        self.container = Gtk.Fixed()
        self.add(self.container)

        self.button = Gtk.Button("Test Button")
        # Add the button in the (x=20,y=100) position
        self.container.put(self.button, 1400, 100)  # ekranın dışına taşıramadığı için butonun yarısını gösteriyor.
        # İstediğimiz şey bu işte !!!!!
        self.container.move(self.button, 1400, 840)  # bu da benzer şekilde move ediyor...

        self.another_button = Gtk.Button("Test Button 22")
        # Add the button in the (x=20,y=100) position
        self.container.put(self.another_button, 400, 100)  # ekranın dışına taşıramadığı için butonun yarısını gösteriyor.

    def add_background_image(self, path=None, x=0, y=0):
        # create an image
        image = Gtk.manage(Gtk.Image())
        # set the content of the image as the file filename.png
        image.set_from_file(path)
        # add the image to the window
        self.container.put(image, x, y)

    def move(self, widget, x=0, y=0):
        self.container.move(widget, x, y)


class Application(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        self.mainWindow = MainWindow(self)
        self.mainWindow.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)


application = Application()
exitStatus = application.run(sys.argv)
sys.exit(exitStatus)
