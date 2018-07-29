import datetime
import gi
import logging
import sys
import time
import select
import Pyro4
import pyautogui

gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, GstVideo, Gtk, GdkPixbuf, Gdk

from ip_checker import get_ip
from remote_command_executer import RemoteCommander  # video player 'ı bu çağırıyor...

logging.basicConfig(filename='network_lost.log', level=logging.DEBUG)

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


class CustomData:
    is_live = None
    pipeline = None
    # main_loop = None  # belki bunu application 'da set ederiz.


# class VideoPlayer:
#     """
#     Simple Video player that just 'plays' a valid input Video file.
#     """
#
#     def __init__(self, uri, moviewindow):
#
#         Gst.init(None)
#         Gst.debug_set_active(True)
#         Gst.debug_set_default_threshold(2)
#
#         self.data = CustomData()
#
#         self.uri = uri
#         self.movie_window = moviewindow
#
#         self.data.pipeline = Gst.ElementFactory.make("playbin", "playbin")
#         self.data.pipeline.set_property("uri", self.uri)
#
#         # rtspsrc kullanırsan aşağıdaki gibi :
#         # self.data.pipeline = Gst.parse_launch(
#         #     "rtspsrc location={} latency=500 timeout=18446744073709551 tcp-timeout=18446744073709551 ! decodebin ! autovideosink".format(self.uri))
#
#         self.streams_list = []
#
#         bus = self.data.pipeline.get_bus()
#
#         ret = self.data.pipeline.set_state(Gst.State.PLAYING)
#         if ret == Gst.StateChangeReturn.FAILURE:
#             print('ERROR: Unable to set the pipeline to the playing state.')
#             sys.exit(-1)
#         elif ret == Gst.StateChangeReturn.NO_PREROLL:
#             print("Buffer oluşturmayacağız data live data...")
#             self.data.is_live = True
#
#         bus.add_signal_watch()
#         bus.enable_sync_message_emission()
#         bus.connect('message', self.cb_message, self.data)
#         bus.connect("sync-message::element", self.on_sync_message)
#         self.data.pipeline.connect('video-changed', self.on_handoff)
#
#     def cb_message(self, bus, msg, data):
#
#         gst_state = self.data.pipeline.get_state(Gst.CLOCK_TIME_NONE)
#
#         # logging.debug("{} state : {}".format(datetime.datetime.now(), gst_state.state.value_name))
#
#         # if gst_state.state.value_name == "GST_STATE_PLAYING":
#         #     print("I am playing")
#
#         t = msg.type
#
#         if t == Gst.MessageType.ERROR:
#             err, debug = msg.parse_error()
#             try:
#                 logging.error('{}\n{}'.format(*err))
#             except:
#                 print('{}'.format(err))
#             self.data.pipeline.set_state(Gst.State.READY)
#             # self.data.main_loop.quit()
#             return
#
#         if t == Gst.MessageType.EOS:
#             # end-of-stream
#             self.data.pipeline.set_state(Gst.State.READY)
#             # self.data.main_loop.quit()
#             return
#
#         if t == Gst.MessageType.BUFFERING:
#             persent = 0
#
#             # If the stream is live, we do not care about buffering.
#             if self.data.is_live:
#                 return
#
#             persent = msg.parse_buffering()
#             print('Buffering {0}%'.format(persent))
#
#             if persent < 100:
#                 self.data.pipeline.set_state(Gst.State.PAUSED)
#             else:
#                 self.data.pipeline.set_state(Gst.State.PLAYING)
#             return
#
#         if t == Gst.MessageType.CLOCK_LOST:
#
#             logging.debug("{} message : Gst.MessageType.CLOCK_LOST".format(datetime.datetime.now()))
#             if gst_state.state.value_name != "GST_STATE_PLAYING":
#                 self.data.pipeline.set_state(Gst.State.PAUSED)
#                 logging.debug("{} message : set paused".format(datetime.datetime.now()))
#             else:
#                 self.data.pipeline.set_state(Gst.State.PLAYING)
#                 logging.debug("{} message : set playing".format(datetime.datetime.now()))
#
#             return
#
#         # while gst_state.state.value_name != "GST_STATE_PLAYING":
#         #     # print("I am not playing, trying to set playing")
#         #     self.data.pipeline.set_state(Gst.State.PLAYING)  # bu yine olmadı
#
#     def on_sync_message(self, bus, message):
#         struct = message.get_structure()
#         if not struct:
#             return
#         message_name = struct.get_name()
#         if message_name == "prepare-window-handle":
#             # Assign the viewport
#             self.imagesink = message.src
#             print("self.imagesink neymiş", self.imagesink)
#             self.imagesink.set_property("force-aspect-ratio", False)
#             self.imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())
#
#     def on_handoff(self, bus, message):
#         print("Handoff oldu ya la!!")


class VideoPlayer:
    """
    Simple Video player that just 'plays' a valid input Video file.
    """

    def __init__(self,
                 rtsp_uri=None,
                 moviewindow=None,
                 video_width=1920,
                 video_height=1080,
                 crop_left=0,
                 crop_right=0,
                 crop_bottom=0,
                 crop_top=0
                 ):
        Gst.init(None)
        Gst.debug_set_active(True)
        Gst.debug_set_default_threshold(2)

        self.data = CustomData()

        self.video_width = video_width
        self.video_height = video_height
        self.crop_left = crop_left
        self.crop_right = crop_right
        self.crop_bottom = crop_bottom
        self.crop_top = crop_top
        self.uri = rtsp_uri
        self.moviewindow = moviewindow

        self.player = None
        self.uridecodebin = None

        # Initialize audio pipeline elements
        self.audioconvert = None
        self.queue2 = None
        self.audiosink = None

        # Initialize video pipeline elements
        self.autoconvert = None
        self.videosink = None
        self.capsfilter = None
        self.videoscale = None
        self.colorspace = None
        self.queue1 = None
        self.videobox = None

        self.construct_pipeline()
        self.is_playing = False
        self.connect_signals()

    def construct_pipeline(self):
        """
        Add and link elements in a GStreamer pipeline.
        """
        # Create uridecodebin instance
        self.uridecodebin = Gst.ElementFactory.make("uridecodebin")
        self.uridecodebin.set_property("uri",
                                       self.uri)

        # Add elements to the pipeline
        self.player.add(self.uridecodebin)

        # Link elements in the pipeline.
        self.player.link(self.uridecodebin)

        self.construct_audio_pipeline()
        self.construct_video_pipeline()

    def construct_audio_pipeline(self):
        """
        Define and link elements to build the audio portion
        of the main pipeline.
        @see: self.construct_pipeline()
        """
        # audioconvert for audio processing pipeline
        self.audioconvert = Gst.ElementFactory.make("audioconvert")
        self.queue2 = Gst.ElementFactory.make("queue")
        self.audiosink = Gst.ElementFactory.make("autoaudiosink")

        self.player.add(self.queue2)
        self.player.add(self.audioconvert)
        self.player.add(self.audiosink)

        self.queue2.link(self.audioconvert)
        self.audioconvert.link(self.audiosink)

    def construct_video_pipeline(self):
        """
        Define and links elements to build the video portion
        of the main pipeline.
        @see: self.construct_pipeline()
        """
        # Autoconvert element for video processing
        self.autoconvert = Gst.ElementFactory.make("videoconvert", "convert")
        print("self.autoconvert", self.autoconvert)
        self.videosink = Gst.ElementFactory.make("autovideosink")

        # Set the capsfilter
        if self.video_width and self.video_height:
            # videocap = Gst.Caps("video/x-raw-yuv," \
            # "width=%d, height=%d"%(self.video_width,
            #                     self.video_height))
            videocap = Gst.Caps.from_string("video/x-raw, width={}, height={}".format(
                self.video_width, self.video_height))

        else:
            videocap = Gst.Caps.from_string("video/x-raw-yuv")

        # Create Capsfilter
        self.capsfilter = Gst.ElementFactory.make("capsfilter")
        self.capsfilter.set_property("caps", videocap)

        # Create Videoscale Element
        self.videoscale = Gst.ElementFactory.make("videoscale")
        self.videoscale.set_property("method", 1)

        # Converts the video from one colorspace to another
        self.colorspace = Gst.ElementFactory.make("videoconvert")

        # Create Video queue
        self.queue1 = Gst.ElementFactory.make("queue")

        # Videobox Element for Crop
        self.videobox = Gst.ElementFactory.make("videobox")
        self.videobox.set_property("bottom", self.crop_bottom)
        self.videobox.set_property("top", self.crop_top)
        self.videobox.set_property("left", self.crop_left)
        self.videobox.set_property("right", self.crop_right)

        # Add elements to the pipeline
        self.player.add(self.queue1)
        self.player.add(self.autoconvert)
        self.player.add(self.videoscale)
        self.player.add(self.videobox)
        self.player.add(self.capsfilter)
        self.player.add(self.colorspace)
        self.player.add(self.videosink)

        # Link elements
        self.queue1.link(self.autoconvert)
        self.autoconvert.link(self.videoscale)
        self.videoscale.link(self.capsfilter)
        self.capsfilter.link(self.videobox)
        self.videobox.link(self.colorspace)
        self.colorspace.link(self.videosink)

        self.player.set_state(Gst.State.PLAYING)

    def connect_signals(self):
        """
        Connects signals with the methods.
        """
        # Capture the messages put on the bus.
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect the decodebin signal
        if self.uridecodebin:
            self.uridecodebin.connect("pad_added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        queue elements, when the decodebin "pad-added" signal
        is generated.
        """
        compatible_pad = None
        caps = pad.query_caps()
        print("caps ney ki?", caps)
        for i in range(caps.get_size()):
            structure = caps.get_structure(i)
            name = structure.get_name()
            print("{0:s}".format(name))
            # print("\n cap name is = ", name)
            if name[:5] == 'video':
                compatible_pad = self.queue1.get_compatible_pad(pad, caps)
            elif name[:5] == 'audio':
                compatible_pad = self.queue2.get_compatible_pad(pad, caps)
                print("burada compatible pad yok mu ki :", compatible_pad)

            if compatible_pad:
                pad.link(compatible_pad)

    # def play(self):
    #     """
    #     Play the media file
    #     """
    #     self.is_playing = True
    #     ret = self.player.set_state(Gst.State.PLAYING)
    #     while self.is_playing:
    #         time.sleep(1)
    #     evt_loop.quit()
    #
    #     if ret == Gst.StateChangeReturn.FAILURE:
    #         print('ERROR: Unable to set the pipeline to the playing state.')
    #         sys.exit(-1)
    #     elif ret == Gst.StateChangeReturn.NO_PREROLL:
    #         print("Buffer oluşturmayacağız data live data...")
    #         self.data.is_live = True

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """

        gst_state = self.player.get_state(Gst.CLOCK_TIME_NONE)

        msg_type = message.type
        if msg_type == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            self.is_playing = False
            print("\n Unable to play Video. Error: ", message.parse_error())
        elif msg_type == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.is_playing = False

        if msg_type == Gst.MessageType.BUFFERING:
            persent = 0
            # If the stream is live, we do not care about buffering.
            if self.data.is_live:
                return

            persent = message.parse_buffering()
            print('Buffering {0}%'.format(persent))

            if persent < 100:
                self.player.set_state(Gst.State.PAUSED)
            else:
                self.player.set_state(Gst.State.PLAYING)
            return

        if msg_type == Gst.MessageType.CLOCK_LOST:

            logging.debug("{} message : Gst.MessageType.CLOCK_LOST".format(datetime.datetime.now()))
            if gst_state.state.value_name != "GST_STATE_PLAYING":
                self.player.set_state(Gst.State.PAUSED)
                logging.debug("{} message : set paused".format(datetime.datetime.now()))
            else:
                self.player.set_state(Gst.State.PLAYING)
                logging.debug("{} message : set playing".format(datetime.datetime.now()))

            return

    def on_sync_message(self, bus, message):
        struct = message.get_structure()
        if not struct:
            return
        message_name = struct.get_name()
        if message_name == "prepare-window-handle":
            # Assign the viewport
            self.imagesink = message.src
            print("self.imagesink neymiş", self.imagesink)
            self.imagesink.set_property("force-aspect-ratio", False)
            self.imagesink.set_window_handle(self.moviewindow.get_property('window').get_xid())


class MainWindow(Gtk.ApplicationWindow):
    # bunun addwidget vb. bir metodu olması lazım task olarak tabii...

    def __init__(self, app):
        Gtk.Window.__init__(self, title=None, application=app)

        # Set the window size
        self.set_size_request(1280, 720)  # bunu settings vb. bir yerden almalı.
        container = Gtk.Fixed()
        self.add(container)


class Application(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

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
        # self.mainWindow.connect("realize", self.realize_cb)

        # titlebar 'ı gizlemek için (hide title bar maximize değilken)
        # self.mainWindow.set_decorated(False)
        #
        self.mainWindow.set_hide_titlebar_when_maximized(True)  # bu da miximize edersen gizle diyor.
        self.mainWindow.fullscreen()  # Full screen yapmak için

        # run function to add image
        self.mainWindow.show_all()
        pyautogui.moveTo(5000, 5000)  # madem ki gizleyemiyoruz o zaman sağ alt köşeye atarız...
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

    def add_source(self, uri, xpos, ypos, width, heigth, name):
        # self.gui.add_source(uri, xpos, ypos, width, heigth, name)
        container = self.gui.mainWindow.get_child()
        videowidget = Gtk.DrawingArea(name=name)
        videowidget.set_halign(Gtk.Align.START)
        videowidget.set_valign(Gtk.Align.START)
        videowidget.set_size_request(width, heigth)
        videowidget.show()
        VideoPlayer(rtsp_uri=uri, moviewindow=videowidget)
        container.put(videowidget, xpos, ypos)


def main():
    Gst.init(None)
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(2)
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

    GObject.threads_init()

    exitStatus = gui.run(sys.argv)

    sys.exit(exitStatus)


if __name__ == "__main__":
    main()

