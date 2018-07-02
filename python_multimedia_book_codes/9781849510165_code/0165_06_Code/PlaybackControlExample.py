#-------------------------------------------------------------------------------
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
#    -  This file, PlaybackControlExample.py is a basic audio processing utility
#       created as an illustration for:
#       Chapter 6 section "Controlling Playback"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  This utility illustrates various Playback controls such as
#       Play, Pause,Stop and seek a position in a track
#    -  Use appropriate flag values such as self.pause_example,
#       self.stop_example , self.seek_example to run various illustrations.
#    - Note: the total audio duration must be greater than 20 seconds.
#---------------
# Dependencies
#---------------
#  In order to run the program the following packages need to be installed and
#  appropriate environment variables need to be set (if it is not done by the
#  installer automatically.)
# 1. Python 2.6
# 2. GStreamer 0.10.5 or later version
# 3. Python bindings for GStreamer v 0.10.15 or later
# 4. PyGObject v 2.14 or later
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
# *Running the program:
#   Replace the value of self.inFileLocation,
#   with appropriate audio file path on your machine.
#   Based on the test you want to conduct, set one of the following flags
#   to True ( be sure to set other flags to False)
#   self.pause_example, self.stop_example , self.seek_example
#
#   Windows user: Be sure to specify the path
#   with forward slashes such as":
#   C:/AudioFiles/audio1.mp3 and NOT like -- C:\AudioFiles\audio1.mp3.
#
#   Then run the program in the command console as:
#
#           $python PlaybackControlExample.py
#
#
#
# TODO:
#   - This is very similar to the code in file AudioEffects.py . Integrate this
#     feature in AudioEffects.py
#
#-------------------------------------------------------------------------------

import time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst
import os


class AudioPlayer:
    """
    This class illustrates use of
    various Playback control functions such as Playing. Pausing, Stopping
    and jumping to a particular in a streaming audio.
    @see: self.play()
    @see: self.runExamples()
    """
    def __init__(self):
        self.duration = None
        self.position = None
        self.is_playing = False

        # Based on the audio control illustration you
        # want to run,set one of the following flags
        # to True (be sure to set other flags to False)
        self.pause_example = False
        self.stop_example  = False
        self.seek_example  = True

        # Flag that ensures that the examples are not accidentaly run
        # more than once.
        self.ranExample = False

        self.constructPipeline()
        self.connectSignals()

    def constructPipeline(self):
        # Create the pipeline instance
        self.player = gst.Pipeline()

        # Define pipeline elements
        self.filesrc = gst.element_factory_make("filesrc")
        self.filesrc.set_property("location", "C:/AudioFiles/audio1.mp3")

        self.decodebin = gst.element_factory_make("decodebin")
        self.audioconvert = gst.element_factory_make("audioconvert")
        self.audiosink = gst.element_factory_make("autoaudiosink")

        # Add elements to the pipeline
        self.player.add(self.filesrc,
                        self.decodebin,
                        self.audioconvert,
                        self.audiosink)

        # Link elements in the pipeline.
        gst.element_link_many(self.filesrc, self.decodebin)
        gst.element_link_many(self.audioconvert, self.audiosink)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # Capture the messages put on the bus.
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)
        # Connect the decodebin signal
        self.decodebin.connect("pad-added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad ):
        """
        Manually link the decodebin pad with a compatible pad on
        audioconvert, when the decodebin element
        generated "pad-added" signal
        """
        caps = pad.get_caps()
        compatible_pad =  self.audioconvert.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

    def play(self):
        """
        Play the music file
        @see: self.runExmples() which is called by this method.
        """
        self.is_playing = True
        self.player.set_state(gst.STATE_PLAYING)
        self.position = None

        while self.is_playing:
            time.sleep(0.5)
            try:
                self.position = (
                        self.player.query_position(gst.FORMAT_TIME,
                                           None) [0] )
            except gst.QueryError:
                # The pipeline is probably reached
                # the end of the audio, (and thus has 'reset' itself.
                # So, it may be unable to query the current position.
                # In this case, do nothing exept to reset
                # self.position to None.
                self.position = None
                pass

            if not self.position is None:
                #Convert the duration into seconds.
                self.position = self.position/gst.SECOND
                print "\n Current playing time: ", self.position

            self.runExamples()
        evt_loop.quit()

    def runExamples(self):
        """
        Run the Playback control examples.
        @see: self.play() which calls this method
        @see: self.runPauseExample()
        @see: self.runStopExample()
        @see: self.runSeekExample()
        """

        if not self.okToRunExamples():
            return

        # The example will be roughly be run when the streaming crosses 5 second
        # mark.
        if self.position >= 5 and self.position < 8:
            if self.pause_example:
                self.runPauseExample()
            elif self.stop_example:
                self.runStopExample()
            elif self.seek_example:
                self.runSeekExample()
            # this flag ensures that an example is run only once.
            self.ranExample = True

    def runPauseExample(self):
        """
        Pauses the audio streaming for 5 seconds and then
        resiumes the playback.
        @see: self.runExamples()
        """
        print ("\n Pause example: Playback will be paused"
                " for 5 seconds and will then be resumed...")
        self.player.set_state(gst.STATE_PAUSED)
        time.sleep(5)
        print "\n .. OK now resuming the playback"
        self.player.set_state(gst.STATE_PLAYING)

    def runStopExample(self):
        """
        Stops the playback after about 5 seconds.
        @see: self.runExamples()
        """
        print ("\n STOP example: Playback will be STOPPED"
        " and then the application will be terminated.")
        self.player.set_state(gst.STATE_NULL)
        self.is_playing = False

    def runSeekExample(self):
        """
        After about 5 seconds of audio streaming, it
        jumps to the position at 15 seconds and the playback
        continues after that.
        @see: self.runExamples()
        """
        print ("\n SEEK example: Now jumping to position at 15 seconds"
        "the audio will continue to stream after this")

        self.player.seek_simple(gst.FORMAT_TIME,
                                  gst.SEEK_FLAG_FLUSH,
                                  15*gst.SECOND)
        self.player.set_state(gst.STATE_PAUSED)
        print "\n starting playback in 2 seconds.."
        time.sleep(2)
        self.player.set_state(gst.STATE_PLAYING)

    def okToRunExamples(self):
        """
        Does some checks to see if it is ok to run the
        examples that illustrate use of various playback controls.
        """
        # If the example has already run, no need to
        # proceed further.
        if self.ranExample:
            return False
        #First get the total duration of the track.
        # it needs to be more than 20 seconds!

        if not self.is_playing:
            print ("\n Error: unable to run example"
            "runExamples() called but audio is not streaming.")
            return False

        if self.duration is None:
            time.sleep(0.2)
            try:
                self.duration = ( self.player.query_duration(gst.FORMAT_TIME,
                                                            None) [0] )
                #Convert the duration into seconds.
                self.duration = self.duration/gst.SECOND
            except gst.QueryError:
                print ("\n ERROR: unable to determine duration."
                "Example not run.")
                return False

        if self.duration < 20:
            print ("\n ERROR: Unable to run Playback Control example."
            "\n Total track duration too short. Needs to be more than "
            "20 seconds. ")
            return False

        #Otherwise return True.
        return True

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False
            print "\n Unable to play audio. Error: ", message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False

# Run the program
player = AudioPlayer()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()






