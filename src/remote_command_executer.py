import gi
import Pyro4
import time

gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gdk, Gst
from playbin_player import VideoPlayer as playbin_player


@Pyro4.expose
class RemoteCommander(object):
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
        # self.gui.move_widget(xpos, ypos, name)
        fixed_widget = self.gui.mainWindow.get_child()
        children = fixed_widget.get_children()
        print(children)
        for child in children:
            print("name :", child.get_name())
            if child.get_name() == name:
                fixed_widget.move(child, xpos, ypos)

    def resize(self, width, height, name):
        fixed_widget = self.gui.mainWindow.get_child()
        children = fixed_widget.get_children()
        print(children)
        for child in children:
            print("name :", child.get_name())

            if child.get_name() == name:
                child.set_size_request(width, height)

    def remove_widget(self, name):
        fixed_widget = self.gui.mainWindow.get_child()
        children = fixed_widget.get_children()
        print(children)
        for child in children:
            print("name :", child.get_name())
            if child.get_name() == name:
                fixed_widget.remove(child)

    def add_source(self, uri, xpos, ypos, width, height, name):
        # self.gui.add_source(uri, xpos, ypos, width, heigth, name)
        container = self.gui.mainWindow.get_child()
        videowidget = Gtk.DrawingArea(name=name)
        videowidget.set_halign(Gtk.Align.START)
        videowidget.set_valign(Gtk.Align.START)
        videowidget.set_size_request(width, height)
        videowidget.show()
        videowidget.player = playbin_player(uri=uri, moviewindow=videowidget)
        videowidget.player.caps = Gst.Caps.from_string("video/x-raw, width={}, height={}".format(
            width, height
        ))
        # videowidget.player.videobox.set_property("bottom", crop_bottom)
        # videowidget.player.videobox.set_property("top", crop_top)
        # videowidget.player.videobox.set_property("left", crop_left)
        # videowidget.player.videobox.set_property("right", crop_right)
        container.put(videowidget, xpos, ypos)

    def change_mod_queue(self,
                         name,
                         width=800,
                         height=600,
                         crop_left=300,
                         crop_right=0,
                         crop_bottom=0,
                         crop_top=0):
        fixed_widget = self.gui.mainWindow.get_child()
        children = fixed_widget.get_children()
        print(children)
        for child in children:
            print("name :", child.get_name())
            if child.get_name() == name:
                print("bakalım player var mı?", child.player)

                child.player.caps = Gst.Caps.from_string("video/x-raw, width={}, height={}".format(
                    width, height
                ))
                child.player.filter = Gst.ElementFactory.make("capsfilter", "filter")
                child.player.filter.set_property("caps", self.caps)
                child.player.videobox.set_property("bottom", crop_bottom)
                child.player.videobox.set_property("top", crop_top)
                child.player.videobox.set_property("left", crop_left)
                child.player.videobox.set_property("right", crop_right)
