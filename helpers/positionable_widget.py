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
        container = Gtk.Fixed()
        self.add(container)

        button = Gtk.Button("Test Button")
        # Add the button in the (x=20,y=100) position
        container.put(button, 1400, 100)  # ekranın dışına taşıramadığı için butonun yarısını gösteriyor.
        # İstediğimiz şey bu işte !!!!!
        container.move(button, 1400, 840)  # bu da benzer şekilde move ediyor...


        another_button = Gtk.Button("Test Button 22")
        # Add the button in the (x=20,y=100) position
        container.put(another_button, 400, 100)  # ekranın dışına taşıramadığı için butonun yarısını gösteriyor.

        # # create an image
        # image = Gtk.Image()
        # # set the content of the image as the file filename.png
        # image.set_from_file("/Users/kemal/WorkSpace/Videowall Development/media/tvlogo_full.png")
        # # add the image to the window
        # container.put(image, 1050, 50)


    def add_image(self, container):
        image = Gtk.Image()
        # set the content of the image as the file filename.png
        image.set_from_file("/Users/kemal/WorkSpace/Videowall Development/media/tvlogo_full.png")
        # add the image to the window
        container.put(image, 1050, 50)

    def add_drawing_area(self, container):
        videowidget = Gtk.DrawingArea()
        container.put(videowidget, 300, 300)


class Application(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        self.mainWindow = MainWindow(self)
        # print(dir(self.mainWindow))
        # get object of fixed widget
        fixed_widget = self.mainWindow.get_child()
        # run function to add image
        self.mainWindow.add_image(fixed_widget)
        self.mainWindow.add_drawing_area(fixed_widget)
        self.mainWindow.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)


application = Application()
exitStatus = application.run(sys.argv)
sys.exit(exitStatus)
