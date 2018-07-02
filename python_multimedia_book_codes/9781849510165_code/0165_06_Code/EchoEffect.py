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
#    -  This file, EchoEffect.py is a basic audio processing utility
#       created as an illustration for:
#       Chapter 6 section "Echo Echo Echo..."
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  A utility that takes an input audio file and adds echo effect
#       to it.
#    -  Illustrates how to selectively add echo effect to the audio
#       using GStreamer Controller object.
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

# @Note: The audioecho plugin should be available in your GStreamer installation.
#       typically this plugin is available in the default GStreamer installation.
#
# *Running the program:
#   Replace the values of self.inFileLocation, self.outFileLocation
#   with appropriate audio file paths on your machine.
#
#   Set appropriate value for flag self.use_echo_controller.
#   Set it to True if you want to add GStreamer controller object to
#   control echo effect.  Setting it to False
#   will run illustration where echo effect is added for the entire
#   audio stream.
#
#   Windows user: Be sure to specify the path
#   with forward slashes such as":
#   C:/AudioFiles/audio1.mp3 and NOT like -- C:\AudioFiles\audio1.mp3.
#
#   Then run the program in the command console as:
#
#           $python EchoEffect.py
#
#   This should create an audio file with echo effect added.
#
# TODO:
#   - This is very similar to the code in file AudioEffects.py . Integrate this
#     feature in AudioEffects.py
#
#-------------------------------------------------------------------------------

import os, sys, time
import thread
import getopt, glob
import gobject
import pygst
pygst.require("0.10")
import gst


class AudioEffects:
    def __init__(self):
        self.is_playing = False
        # Flag used for printing purpose only.
        self.error_msg = ''

        #the flag that determines whether to use
        # a gst Controller object to adjust the
        # intensity of echo while playing the audio.
        self.use_echo_controller = False

        self.inFileLocation = "C:/AudioFiles/audio1.mp3"
        self.outFileLocation = "C:/AudioFiles/audio1_out.mp3"

        self.constructPipeline()
        self.connectSignals()

    def constructPipeline(self):
        """
        Create a GStreamer pipeline.
        """
        self.pipeline = gst.Pipeline()

        self.filesrc = gst.element_factory_make("filesrc")
        self.filesrc.set_property("location", self.inFileLocation)

        self.decodebin = gst.element_factory_make("decodebin")

        self.audioconvert = gst.element_factory_make("audioconvert")
        self.audioconvert2 = gst.element_factory_make("audioconvert")

        self.encoder = gst.element_factory_make("lame")

        self.filesink = gst.element_factory_make("filesink")
        self.filesink.set_property("location", self.outFileLocation)


        self.echo = gst.element_factory_make("audioecho")
        self.echo.set_property("delay", 1*gst.SECOND)
        self.echo.set_property("feedback", 0.3)

        if self.use_echo_controller:
            self.setupEchoControl()
        else:
            self.echo.set_property("intensity", 0.5)

        self.pipeline.add(self.filesrc,
                          self.decodebin,
                          self.audioconvert,
                          self.echo,
                          self.audioconvert2,
                          self.encoder,
                          self.filesink)


        gst.element_link_many( self.filesrc, self.decodebin)
        gst.element_link_many(self.audioconvert,
                              self.echo,
                              self.audioconvert2,
                              self.encoder,
                              self.filesink)

    def setupEchoControl(self):
        """
        Setup the gst.Controller object to adjust the
        intensity of the audio echo.
        """
        self.echoControl = gst.Controller(self.echo, "intensity")
        self.echoControl.set("intensity", 0*gst.SECOND, 0.5)
        self.echoControl.set("intensity", 4*gst.SECOND, 0.0)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # capture the messages put on the bus.
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)
        self.decodebin.connect("pad_added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad ):
        """
        Manually link the decodebin pad with a compatible pad on
        audioconvert, when the decodebin element generated "pad_added" signal
        """
        caps = pad.get_caps()
        compatible_pad =  self.audioconvert.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)


    def play(self):
        """
        Start streaming the audio
        @see: self.addFadingEffect()
        """
        self.is_playing = True
        self.pipeline.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)
        self.printFinalStatus()
        evt_loop.quit()

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False
            self.error_msg =  message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False

    def printFinalStatus(self):
        """
        Print final status message.
        """
        if self.error_msg:
            print "\n ", self.error_msg
        else:
            print "\n Done adding effect. "
            print "\n The audio written to: ", self.outFileLocation

# Run the program
player = AudioEffects()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()
