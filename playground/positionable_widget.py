import gi
from random import randint
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
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
        button.set_name("ilk buton")
        # Add the button in the (x=20,y=100) position
        container.put(button, 1400, 100)  # ekranın dışına taşıramadığı için butonun yarısını gösteriyor.
        # İstediğimiz şey bu işte !!!!!
        container.move(button, 1400, 840)  # bu da benzer şekilde move ediyor...

        another_button = Gtk.Button("Test Button 22")
        another_button.set_name("ikinci buton")
        # Add the button in the (x=20,y=100) position
        container.put(another_button, 400, 100)  # ekranın dışına taşıramadığı için butonun yarısını gösteriyor.

        # # create an image
        # image = Gtk.Image()
        # # set the content of the image as the file filename.png
        # image.set_from_file("/Users/kemal/WorkSpace/Videowall Development/media/tvlogo_full.png")
        # # add the image to the window
        # container.put(image, 1050, 50)

    def add_image(self, widget_name="test resmi", path=None, pos_x=0, pos_y=0):
        print("add_image_çalıştı")
        container = self.get_child()
        image = Gtk.Image(name=widget_name)
        if path:
            # set the content of the image as the file filename.png
            image.set_from_file(path)
        else:
            image.set_from_file("/Users/kemal/WorkSpace/Videowall Development/media/tvlogo_full.png")

        if pos_x > 0 and pos_y > 0:
            # add the image to the window
            container.put(image, pos_x, pos_y)
        else:
            pos_x = randint(-200, 1500)
            pos_y = randint(-200, 850)
            container.put(image, pos_x, pos_y)

        self.show_all()

    def add_drawing_area(self):
        container = self.get_child()
        videowidget = Gtk.DrawingArea()
        container.put(videowidget, 300, 300)


class Application(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        self.mainWindow = MainWindow(self)
        # get object of fixed widget
        fixed_widget = self.mainWindow.get_child()
        # run function to add image
        self.mainWindow.add_image()
        self.mainWindow.add_drawing_area()
        self.mainWindow.show_all()
        #  this takes 2 args: (how often to update in millisec, the method to run)
        GObject.timeout_add(5000, self.remove_widget)
        GObject.timeout_add(10000, self.add_image)
        GObject.timeout_add(15000, self.add_image)
        GObject.timeout_add(25000, self.add_image)
        GObject.timeout_add(30000, self.add_image)
        GObject.timeout_add(35000, self.add_image)
        GObject.timeout_add(40000, self.add_image)

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def add_image(self):
        fixed_widget = self.mainWindow.get_child()
        self.mainWindow.add_image(fixed_widget)

    def remove_widget(self, name="test resmi"):
        fixed_widget = self.mainWindow.get_child()
        children = fixed_widget.get_children()
        print(children)
        for child in children:
            print("name :", child.get_name())

            if child.get_name() == name:
                fixed_widget.remove(child)


application = Application()
exitStatus = application.run(sys.argv)
sys.exit(exitStatus)
