import gi
from random import randint

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GdkPixbuf, Gdk, Gst
import sys
import time
import select
import Pyro4

# from src.playbin_player import VideoPlayer as playbin_player
from src.ip_checker import get_ip
from src.remote_command_executer import RemoteCommander

IP = get_ip()

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
        self.set_size_request(800, 450)  # bunu settings vb. bir yerden almalı.
        # self.overlay = Gtk.Overlay()
        # self.add(self.overlay)
        # self.background = Gtk.Image.new_from_file('/Users/kemal/WorkSpace/Videowall Development/media/tvlogo_full.png')
        # self.overlay.add(self.background)

        # self.get_window().set_decorations(Gdk.WMDecoration.BORDER)

        # Add GtkFixed to the main window
        container = Gtk.Fixed()
        self.add(container)
        """
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
        """
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

        # run function to add image
        self.mainWindow.show_all()
        #  this takes 2 args: (how often to update in millisec, the method to run)
        # GObject.timeout_add(5000, self.resize_widget)
        # GObject.timeout_add(10000, self.resize_widget)
        # GObject.timeout_add(15000, self.resize_widget)
        # GObject.timeout_add(20000, self.resize_widget)
        # GObject.timeout_add(25000, self.resize_widget)
        # GObject.timeout_add(10000, self.add_image)
        # GObject.timeout_add(15000, self.add_image)
        # GObject.timeout_add(25000, self.add_image)
        # GObject.timeout_add(30000, self.add_image)
        # GObject.timeout_add(35000, self.add_image)
        # GObject.timeout_add(40000, self.add_image)

    def do_startup(self):
        Gst.init(None)
        Gtk.Application.do_startup(self)

    def add_message(self, message):
        message = "[{0}] {1}".format(time.strftime("%X"), message)
        print(message)
        # self.serveroutput.append(message)
        # self.serveroutput = self.serveroutput[-27:]
        # self.msg.config(text="\n".join(self.serveroutput))



# application = Application()
#
# exitStatus = application.run(sys.argv)
#
# sys.exit(exitStatus)

def main():
    gui = Application()

    # create a pyro daemon with object

    daemon = Pyro4.Daemon(host=IP)
    obj = RemoteCommander(gui)
    ns = Pyro4.locateNS()
    uri = daemon.register(obj)
    ns.register(IP, uri)

    gui.install_pyro_event_callback(daemon)
    urimsg = "Pyro object uri = {0}".format(uri)
    print(urimsg)

    # add a Pyro event callback to the gui's mainloop
    exitStatus = gui.run(sys.argv)

    sys.exit(exitStatus)


if __name__ == "__main__":
    main()
