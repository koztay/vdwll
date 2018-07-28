#!/usr/local/bin/python
# coding: utf-8
# -------------------------------------------------------------------------------

"""
Bu dosya UBUNTU DELL 'de çalışıyor. "rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov"
linkini sorunsuz oynatıyor. Kamera linkini nasıl test ederim??? Bu MAc 'te de çalıştı.
IP Camera olarak Cep tele program yükledim ve çalıştı. Mac'te crop ediyor ama resize
etmiyor gibi çalışıyor sanki. DELL 'de henüz kontrol edemedim.

        # self.inFileLocation = "../../../media/webos.mp4"
        # self.inFileLocation = "/home/kemal/Developer/vdwll/media/brbad.mp4"
        # "/../../../media/pixar.mp4"

        # self.uri = "https://www.freedesktop.org/software/gstreamer-sdk/data/media/sintel_trailer-480p.webm"
        # self.uri = "rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov"
        # self.uri = "rtsp://127.0.0.1:8554/test"
        # self.uri = "rtsp://192.168.1.32:5540/ch0"
        # self.uri = "http://192.168.1.32:8080/playlist.m3u"

"""
import datetime
import gi
import logging
import sys
import time
import threading


gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst, GObject, Gtk


class CustomData:
    is_live = None
    pipeline = None
    # main_loop = None  # belki bunu application 'da set ederiz.


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
        self.uri = uri

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

        # Create the pipeline instance
        self.player = Gst.Pipeline()

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

    def play(self):
        """
        Play the media file
        """
        self.is_playing = True
        ret = self.player.set_state(Gst.State.PLAYING)
        while self.is_playing:
            time.sleep(1)
        evt_loop.quit()

        if ret == Gst.StateChangeReturn.FAILURE:
            print('ERROR: Unable to set the pipeline to the playing state.')
            sys.exit(-1)
        elif ret == Gst.StateChangeReturn.NO_PREROLL:
            print("Buffer oluşturmayacağız data live data...")
            self.data.is_live = True

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


if __name__ == "__main__":
    # uri = "rtsp://78.188.204.20/media/video1"  # compatible pad bulamıyor macte
    # uri = "rtsp://192.168.1.32:5540/ch0" # cep tel linki
    uri = "rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov"
    # uri = "https://www.freedesktop.org/software/gstreamer-sdk/data/media/sintel_trailer-480p.webm"
    # yukarıdaki webm urisi Mac'te No decoder available for type 'audio/x-vorbis, ....
    # uyarısı verip takılıyor. Ancak constuct_audio_pipeline 'ı (line 112) kapatınca çalışıyor.
    Gst.init(None)
    Gst.debug_set_colored(Gst.DebugColorMode.ON)
    Gst.debug_set_active(True)
    Gst.debug_set_default_threshold(2)
    player = VideoPlayer(rtsp_uri=uri, video_width=800, video_height=600)
    thread = threading.Thread(target=player.play)
    thread.start()
    GObject.threads_init()
    evt_loop = GObject.MainLoop()
    evt_loop.run()
