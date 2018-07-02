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
#    -  This file, AudioEffects.py is a basic audio processing utility
#       created as an illustration for:
#       Chapter 6 sections "Adjusting Volume" and "Fading Effects"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    -  A utility that takes an input audio file and modifies the
#       volume level and saves the resultant file. See method
#       AudioEffects.construct_pipeline() for more details.
#    -  If the flag self.fade_example is set to true, instead of adjusting
#       the volume, it adds a fade out effect when the audio approaches
#       its end. See method AudioEffects.addFadingEffect() for more details.
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
#   Replace the values of self.inFileLocation, self.outFileLocation
#   with appropriate audio file paths on your machine.
#
#   Set appropriate value for flag self.fade_example.
#   Set it to True if you want fading effects to the audio. Setting it to False
#   will run illustration  for adjusting volume. In the latter case,
#   tweak the value of self.volumeLevel to get a desired volume level
#   in the output audio.
#
#   Windows user: Be sure to specify the path
#   with forward slashes such as":
#   C:/AudioFiles/audio1.mp3 and NOT like -- C:\AudioFiles\audio1.mp3.
#
#   Then run the program in the command console as:
#
#           $python AudioEffects.py
#
#   This should create an audio file with adjusted volume or fading effect.
#
# TODO:
#   - GStreamer documentation has a note that says
#     gst.Controller.set_interpolation_mode is deprecated. Use gst.ControlSource
#     or gst.InterpolationControlSource directly to control elements.
#     When gst.InterpolationControlSource was used, I was unable to call
#     the method gst.InterpolationControlSource.set() which can be used to
#     set the volume at certain points in the timeline. But then it gave an
#     attribute error for  gst.InterpolationControlSource.set. But the
#     gstreamer documentation lists this as a known attribute! Not sure if
#     it is an unsupported attribute in my current version of Python bindings
#     of GStreamer/ or GStreamer or some other error. Tried the following:
#
#        self.volumeControlSource = gst.InterpolationControlSource()
#        self.volumeControl.set_control_source("volume",
#                                              self.volumeControlSource)
#        self.volumeControlSource.set_interpolation_mode(gst.INTERPOLATE_LINEAR)
#        self.volumeControlSource.set(fade_start * gst.SECOND,
#                               fade_volume)
#        self.volumeControlSource.set(fade_end * gst.SECOND,
#                               fade_volume*0.01)
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
        self.fade_example = False

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
        self.encoder = gst.element_factory_make("lame")

        self.filesink = gst.element_factory_make("filesink")
        self.filesink.set_property("location", self.outFileLocation)

        self.volume = gst.element_factory_make("volume")

        # You can change the value of self.volumeLevel and see
        # how it affects the output audio.
        self.volumeLevel = 2.0

        if self.fade_example:
            # Set the gst.Controller object for adjusting
            # volume level.
            self.setupVolumeControl()
        else:
            # Adjust the volume only.
            self.volume.set_property("volume", self.volumeLevel)


        self.pipeline.add(self.filesrc,
                          self.decodebin,
                          self.audioconvert,
                          self.volume,
                          self.encoder,
                          self.filesink)

        gst.element_link_many( self.filesrc, self.decodebin)
        gst.element_link_many(self.audioconvert,
                              self.volume,
                              self.encoder,
                              self.filesink)

    def setupVolumeControl(self):
        """
        Setup the gst.Controller object to adjust the volume.
        @todo: See a TODO comment about use of
              Controller.set_interpolation_mode()
        """
        self.volumeControl = gst.Controller(self.volume, "volume")
        self.volumeControl.set("volume", 0.0*gst.SECOND, self.volumeLevel)
        # Alternatively, try gst.INTERPOLATE_CUBIC to see how it affects
        # the fading effect.
        self.volumeControl.set_interpolation_mode("volume",
                                                  gst.INTERPOLATE_LINEAR)
    def addFadingEffect(self):
        """
        Add the fade-out effect. It needs to query the track duration
        Therefore, the pipeline must be in a playing state.
        @see: self.play() where it is called.
        """
        # Fist make sure that we can add the fading effect!
        if not self.is_playing:
            print ("\n Error: unable to add fade effect"
                   "addFadingEffect() called erroniously")
            return

        time.sleep(0.1)
        try:
            duration = ( self.pipeline.query_duration(gst.FORMAT_TIME,
                                         None) [0] )
            #Convert the duration into seconds.
            duration = duration/gst.SECOND
        except gst.QueryError:
            print ("\n Error: unable to determine duration."
                   "Fading effect not added.")
            return

        if duration < 4:
            print ("ERROR: unable to add fading effect."
                   "\n duration too short.")
            return

        fade_start = duration - 4
        fade_volume = self.volumeLevel
        fade_end = duration

        self.volumeControl.set("volume",
                               fade_start * gst.SECOND,
                               fade_volume)

        self.volumeControl.set("volume",
                               fade_end * gst.SECOND,
                               fade_volume*0.01)

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

        # Add fad-out effect if asked for.
        if self.fade_example:
            self.addFadingEffect()

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
            print "\n Done adding effects/ adjusting volume "
            print "\n The audio written to: ", self.outFileLocation

# Run the program
player = AudioEffects()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()
