#-------------------------------------------------------------------------------
# @author: Ninad Sathaye
# @copyright: 2010, Ninad Sathaye email:ninad.consult@gmail.com.
# @license: This  program is distributed under the terms of the
#           GNU General Public License GPLv3 or any later version.
#           See http://www.gnu.org/licenses/gpl-3.0.html for more details.
# @summary:
#    -  This file, SeparatingAudio.py is a utility that separates out
#       the audio and video tracks from an input video file.
#       created as an illustration for Chapter 7 section:
#       "Separating Audio and Video Tracks"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    - This program illustrates how to separate audio and video tracks from
#      a video file and save them as separate files.
#    - See program running instructions below.
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
# 5. The following is a partial list of GStreamer plug-ins
#   that should be available in your GStreamer installation. Typically
#   these plug-ins are available by default. If not, install those.
#   lame, ffmux_mp4, ffenc_mpeg4,
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
# *Running the program:
#   Replace values of self.inFileLocation, self.audioOutLocation and
#    self.videoOutLocation with appropriate path strings and then run the
#    program from the command console as:
#
#           $python SeparatingAudio.py
# @TODO:
#   - Add support for command line arguments.
#   - Support more video file formats. At present, it saves the video track in
#     as mp4 format and  the audio track in mp3 audio format.
#-------------------------------------------------------------------------------

import time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst
import os

class AudioSeparator:
    """
    Utility that separates the audio and video tracks from
    an input video file.
    """
    def __init__(self):
        self.use_parse_launch = False
        self.decodebin = None
        self.error_msg = ''
        # Replace these paths with appropriate file paths on your
        # machine.
        self.inFileLocation="C:/VideoFiles/my_music.mp4"
        self.audioOutLocation="C:/VideoFiles/audioOut.mp3"
        self.videoOutLocation="C:/VideoFiles/videoOut.mp4"

        self.constructPipeline()
        self.is_playing = False
        self.connectSignals()

    def constructPipeline(self):
        """
        Create the pipeline, add and link elements.
        """
        # Create the pipeline instance
        self.player = gst.Pipeline()

        # Define pipeline elements
        self.filesrc = gst.element_factory_make("filesrc")

        self.filesrc.set_property("location", self.inFileLocation)

        self.decodebin = gst.element_factory_make("decodebin")

        self.autoconvert = gst.element_factory_make("autoconvert")

        self.audioconvert = gst.element_factory_make("audioconvert")
        self.audioresample = gst.element_factory_make("audioresample")
        self.audio_encoder = gst.element_factory_make("lame")
        self.audiosink = gst.element_factory_make("filesink")
        self.audiosink.set_property("location", self.audioOutLocation)

        self.video_encoder = gst.element_factory_make("ffenc_mpeg4")
        self.muxer = gst.element_factory_make("ffmux_mp4")

        self.videosink = gst.element_factory_make("filesink")
        self.videosink.set_property("location", self.videoOutLocation)

        self.queue1 = gst.element_factory_make("queue")
        self.queue2 = gst.element_factory_make("queue")
        self.queue3 = gst.element_factory_make("queue")

        # Add elements to the pipeline
        self.player.add(self.filesrc,
                        self.decodebin,
                        self.queue1,
                        self.autoconvert,
                        self.video_encoder,
                        self.muxer,
                        self.videosink,
                        self.queue2,
                        self.audioconvert,
                        self.audio_encoder,
                        self.audiosink,
                        self.queue3
                        )

        # Link elements in the pipeline.
        gst.element_link_many(self.filesrc, self.decodebin)

        gst.element_link_many(self.queue1,
                              self.autoconvert,
                              self.video_encoder,
                              self.muxer,
                              self.videosink)

        gst.element_link_many(self.queue2,
                              self.audioconvert,
                              self.audio_encoder,
                              self.audiosink)

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
        queue elements, when the decodebin element generated "pad_added" signal
        """
        compatible_pad = None
        caps = pad.get_caps()
        name = caps[0].get_name()
        print "\n cap name is = ", name
        if name[:5] == 'video':
            compatible_pad = self.queue1.get_compatible_pad(pad, caps)
        elif name[:5] == 'audio':
            compatible_pad = self.queue2.get_compatible_pad(pad, caps)

        if compatible_pad:
            pad.link(compatible_pad)


    def play(self):
        """
        Start streaming the media.
        @see: self.construct_pipeline() which defines a
        pipeline that does the job of separating audio and
        video tracks.
        """
        starttime = time.clock()

        self.is_playing = True
        self.player.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)
        endtime = time.clock()
        self.printFinalStatus(starttime, endtime)
        evt_loop.quit()

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False
            self.error_msg =  message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False

    def printFinalStatus(self, starttime, endtime):
        """
        Print the final status message.
        """

        if self.error_msg:
            print self.error_msg
        else:
            print "\n Done!"
            print "\n Audio and video tracks separated and saved as "\
            "following files"
            print "\n audio:%s \n video:%s"%(self.audioOutLocation,
                                            self.videoOutLocation)
            print "\n Approximate time required :  \
            %.4f seconds" % (endtime - starttime)

# Run the program
player = AudioSeparator()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()

