# -------------------------------------------------------------------------------
# @author: Ninad Sathaye
# @copyright: 2010, Ninad Sathaye email:ninad.consult@gmail.com.
# @license: This program is free software: you can redistribute it and/or modify
#           it under the terms of the GNU General Public License as published by
#           the Free Software Foundation, either version 3 of the License, or
#           (at your option) any later version.
#
#           This program is distributed in the hope that it will be useful,
#           but WITHOUT ANY WARRANTY; without even the implied warranty of
#           MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#           GNU General Public License for more details.
#
#           You should have received a copy of the GNU General Public License
#           along with this program.  If not, see <http://www.gnu.org/licenses/>.
# @summary:
#    -  This file, PlayingAudio.py is a basic Audio Player utility
#       created as an illustration for Chapter 5 section "Playing Audio"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
# -------------
# Details
# -------------
#    -  A simple audio player program that "plays"
#       the given audio file. It must be a valid audio format, recognizable
#       by decodebin plugin.
#    - This example covers several fundamental concepts of using
#      Gstreamer Python bindings for basic audio processing.
#    - Especially, it shows how to use Gst.parse_launch() to construct
#      a Gst Pipeline instance. To use this method, set the flag
#      self.use_parse_launch to True in the __init__ method.
#    - The program also illustrates how to construct a Gst.Pipeline by creating
#     and linking various element objects. To use this way, set the flag
#      self.use_parse_launch to False in the __init__ method .
#     - Among many other things, it
#      also illustrates basic message handling by connecting bus signal.
# ---------------
# Dependencies
# ---------------
#  In order to run the program the following packages need to be installed and
#  appropriate environment variables need to be set (if it is not done by the
#  installer automatically.)
# 1. Python 2.6
# 2. Gstreamer 0.10.5 or later version
# 3. Python bindings for Gstreamer v 0.10.15 or later
# 4. PyGObject v 2.14 or later
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
# *Running the program:
#   Replace C:/AudioFiles/my_music.mp3 in the construct_pipeline() method ,
#   with a valid audio file path. Then run the program in the command console as:
#
#           $python PlayingAudio.py
#
# -------------------------------------------------------------------------------

import threading
import time
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject


class AudioPlayer:
    """
    Simple audio player that just 'plays' a valid input audio file.
    """

    def __init__(self):
        self.use_parse_launch = False  # True yapınca pipeline string ile çalışmıyor.
        self.decodebin = None

        self.constructPipeline()
        self.is_playing = False
        self.connectSignals()

    def constructPipeline(self):
        if self.use_parse_launch:
            myPipelineString = (
                "filesrc location='/Users/kemal/WorkSpace/Videowall Development/media/si_se_the_truth.mp3' "
                "! decodebin ! audioconvert ! autoaudiosink")
            self.player = Gst.parse_launch(myPipelineString)
        else:
            # Create the pipeline instance
            self.player = Gst.Pipeline()

            # Define pipeline elements
            self.filesrc = Gst.ElementFactory.make("filesrc")

            self.filesrc.set_property("location",
                                      "/Users/kemal/WorkSpace/Videowall Development/media/si_se_the_truth.mp3")

            # Note: the decodebin signal is connected in self.connectSignals()
            self.decodebin = Gst.ElementFactory.make("decodebin", "decodebin")

            self.audioconvert = Gst.ElementFactory.make("audioconvert",
                                                        "audioconvert")

            self.audiosink = Gst.ElementFactory.make("autoaudiosink",
                                                     "a_a_sink")

            # Add elements to the pipeline
            self.player.add(self.filesrc, self.decodebin,
                            self.audioconvert, self.audiosink)

            # Link elements in the pipeline.
            # Gst.element_link_many(self.filesrc, self.decodebin)
            self.filesrc.link(self.decodebin)
            # Gst.element_link_many(self.audioconvert, self.audiosink)
            self.audioconvert.link(self.audiosink)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # Capture the messages put on the bus.
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect the decodebin signal
        if not self.decodebin is None:
            self.decodebin.connect("pad_added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        audioconvert, when the decodebin element emits "pad-added" signal
        """
        caps = pad.query_caps(None)
        compatible_pad = self.audioconvert.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

    def play(self):
        """
        Play the music file
        """
        self.is_playing = True
        self.player.set_state(Gst.State.PLAYING)
        while self.is_playing:
            time.sleep(1)
        evt_loop.quit()

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            self.is_playing = False
            print("\n Unable to play audio. Error: ", message.parse_error())
        elif msgType == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.is_playing = False


# Init Gstreamer
Gst.init(None)

# Run the program
player = AudioPlayer()
# thread.start_new_thread(player.play, ())
thread = threading.Thread(target=player.play)
thread.start()
GObject.threads_init()
evt_loop = GObject.MainLoop()
evt_loop.run()
