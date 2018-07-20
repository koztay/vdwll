import gi
from random import randint
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GdkPixbuf, Gdk, Gst
import sys
import time
import select
import Pyro4

from playbin_player import VideoPlayer as playbin_player


"""
Not: 
$ pyro4-ns -n 0.0.0.0 -p 9999
vb. bir komut ile nameserver başlatmak lazım. 
Aksi taktirde eğer nameserver yoksa iletişim de yok...
Ya da nameserver olmadan uri 'ye IP adresi yazmak lazım.
Bu şekilde oluyor mu denemedim...

"""


# Set the Pyro servertype to the multiplexing select-based server that doesn't
# use a threadpool to service method calls. This way the method calls are
# handled inside the main thread as well.
Pyro4.config.SERVERTYPE = "multiplex"

# The frequency with which the GUI loop calls the Pyro event handler.
PYRO_EVENTLOOP_HZ = 50


class MainWindow(Gtk.ApplicationWindow):
    # bunun addwidget vb. bir metodu olması lazım task olarak tabii...

    def __init__(self, app):
        Gtk.Window.__init__(self, title=None, application=app)

        # Set the window size
        self.set_size_request(1440, 200)  # bunu settings vb. bir yerden almalı.
        # self.overlay = Gtk.Overlay()
        # self.add(self.overlay)
        # self.background = Gtk.Image.new_from_file('/Users/kemal/WorkSpace/Videowall Development/media/tvlogo_full.png')
        # self.overlay.add(self.background)

        # self.get_window().set_decorations(Gdk.WMDecoration.BORDER)

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

        # create scalable image for background
        # create pixbuf
        """
        pixbuf = GdkPixbuf.Pixbuf.new_from_file('../media/tvlogo_full.png')
        # resize it:
        pixbuf = pixbuf.scale_simple(2500, 2000, GdkPixbuf.InterpType.BILINEAR)
        # create an image
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        # add the image to the window
        container.put(image, 0, 0)
        container.move(image, 200, 200)  # move da çalışıyor işte...
        """

        """
        Using scale_simple() does not preserve aspect ratio.
        Using new_from_file_at_size() preserves aspect ratio
        """

        """       
       
        # bı da crop edip sonra resize etmek için
        # GdkPixbuf.Pixbuf.new_subpixbuf(sourcepixbuf, startx, starty, width, height)
        cropped_buffer = GdkPixbuf.Pixbuf.new_subpixbuf(pixbuf, 1000, 1200, 200, 200)  # öncesinde resize edildiği için
        image2 = Gtk.Image()
        image2.set_from_pixbuf(cropped_buffer)
        # add the image to the window
        container.put(image2, -100, -100)
        """

    def add_image(self, widget_name="test resmi", path=None, pos_x=0, pos_y=0):
        print("add_image_çalıştı func içinden")
        container = self.get_child()
        image = Gtk.Image(name=widget_name)
        if path:
            # set the content of the image as the file filename.png
            image.set_from_file(path)
        else:
            image.set_from_file("../media/tvlogo_full.png")

        if pos_x > 0 and pos_y > 0:
            # add the image to the window
            container.put(image, pos_x, pos_y)
        else:
            pos_x = randint(-200, 1500)
            pos_y = randint(-200, 850)
            container.put(image, pos_x, pos_y)


    def add_rtsp_source(self):
        container = self.get_child()

        videowidget = Gtk.DrawingArea(name="video src")

        videowidget.set_halign(Gtk.Align.START)
        videowidget.set_valign(Gtk.Align.START)
        videowidget.set_size_request(640, 480)
        videowidget.show()

        player = playbin_player(uri="rtsp://10.0.0.143/media/video1", moviewindow=videowidget)
        player.play()
        container.put(videowidget, 500, 400)
        self.show_all()


class Application(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)
        GObject.threads_init()


    def install_pyro_event_callback(self, daemon):
        """
        Add a callback to the tkinter event loop that is invoked every so often.
        The callback checks the Pyro sockets for activity and dispatches to the
        daemon's event process method if needed.
        """

        def pyro_event():
            while True:
                # for as long as the pyro socket triggers, dispatch events
                s, _, _ = select.select(daemon.sockets, [], [], 0.01)
                if s:
                    daemon.events(s)
                else:
                    # no more events, stop the loop, we'll get called again soon anyway
                    break
            GObject.timeout_add(1000 // PYRO_EVENTLOOP_HZ, pyro_event)

        GObject.timeout_add(1000 // PYRO_EVENTLOOP_HZ, pyro_event)

    def do_activate(self):
        self.mainWindow = MainWindow(self)

        # titlebar 'ı gizlemek için (hide title bar maximize değilken)
        # self.mainWindow.set_decorated(False)
        #
        # self.mainWindow.set_hide_titlebar_when_maximized(True)  # bu da miximize edersen gizle diyor.
        # self.mainWindow.fullscreen()  # Full screen yapmak için

        # get object of fixed widget
        fixed_widget = self.mainWindow.get_child()
        # run function to add image
        self.mainWindow.add_image()
        self.mainWindow.add_rtsp_source()
        self.mainWindow.show_all()
        #  this takes 2 args: (how often to update in millisec, the method to run)
        GObject.timeout_add(5000, self.resize_widget)
        GObject.timeout_add(10000, self.resize_widget)
        GObject.timeout_add(15000, self.resize_widget)
        GObject.timeout_add(20000, self.resize_widget)
        GObject.timeout_add(25000, self.resize_widget)
        # GObject.timeout_add(10000, self.add_image)
        # GObject.timeout_add(15000, self.add_image)
        # GObject.timeout_add(25000, self.add_image)
        # GObject.timeout_add(30000, self.add_image)
        # GObject.timeout_add(35000, self.add_image)
        # GObject.timeout_add(40000, self.add_image)

    def do_startup(self):
        Gst.init(None)
        Gtk.Application.do_startup(self)


    def add_image(self):
        fixed_widget = self.mainWindow.get_child()
        self.mainWindow.add_image(fixed_widget)
        return "add image çalıştı return olarak"

    def remove_widget(self, name="test resmi"):
        fixed_widget = self.mainWindow.get_child()
        children = fixed_widget.get_children()
        print(children)
        for child in children:
            print("name :", child.get_name())

            if child.get_name() == name:
                fixed_widget.remove(child)

    def move_widget(self, xpos, ypos, name):
        fixed_widget = self.mainWindow.get_child()
        children = fixed_widget.get_children()
        print(children)
        for child in children:
            print("name :", child.get_name())
            if child.get_name() == name:
                fixed_widget.move(child, xpos, ypos)

    def resize_widget(self, width=800, height=450, name="video src"):
        fixed_widget = self.mainWindow.get_child()
        children = fixed_widget.get_children()
        print(children)
        for child in children:
            print("name :", child.get_name())

            if child.get_name() == name:
                width = randint(100, 1500)
                height = randint(100, 850)
                child.set_size_request(width, height)

    def add_message(self, message):
        message = "[{0}] {1}".format(time.strftime("%X"), message)
        print(message)
        # self.serveroutput.append(message)
        # self.serveroutput = self.serveroutput[-27:]
        # self.msg.config(text="\n".join(self.serveroutput))


@Pyro4.expose
class MessagePrinter(object):
    """
    The Pyro object that interfaces with the GUI application.
    """

    def __init__(self, gui):
        self.gui = gui

    def message(self, messagetext):
        # Add the message to the screen.
        # Note that you can't do anything that requires gui interaction
        # (such as popping a dialog box asking for user input),
        # because the gui (tkinter) is busy processing this pyro call.
        # It can't do two things at the same time when embedded this way.
        # If you do something in this method call that takes a long time
        # to process, the GUI is frozen during that time (because no GUI update
        # events are handled while this callback is active).
        self.gui.add_message("from Pyro: " + messagetext)

    def sleep(self, duration):
        # Note that you can't perform blocking stuff at all because the method
        # call is running in the gui mainloop thread and will freeze the GUI.
        # Try it - you will see the first message but everything locks up until
        # the sleep returns and the method call ends
        self.gui.add_message("from Pyro: sleeping {0} seconds...".format(duration))
        time.sleep(duration)
        self.gui.add_message("from Pyro: woke up!")

    def add_image(self):
        self.gui.add_image()

    def move_widget(self, xpos, ypos, name):
        self.move_widget(xpos, ypos, name)


# application = Application()
#
# exitStatus = application.run(sys.argv)
#
# sys.exit(exitStatus)

def main():
    gui = Application()

    # create a pyro daemon with object

    daemon = Pyro4.Daemon(host="10.0.0.30")
    obj = MessagePrinter(gui)
    ns = Pyro4.locateNS()
    uri = daemon.register(obj)
    ns.register("videowall_agent_1", uri)

    gui.install_pyro_event_callback(daemon)
    gui.add_message("Pyro server started. Not using threads.")
    gui.add_message("Use the command line client to send messages.")
    urimsg = "Pyro object uri = {0}".format(uri)
    gui.add_message(urimsg)
    print(urimsg)

    # add a Pyro event callback to the gui's mainloop
    exitStatus = gui.run(sys.argv)

    sys.exit(exitStatus)


if __name__ == "__main__":
    main()

