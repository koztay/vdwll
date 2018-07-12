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
#    -  This file, ImagesFromVideo.py is a utility that can take N number
#       of still images from a streaming video in a specified time frame.
#       It is created as an illustration for Chapter 7 section,
#       "Saving Video Frames as Images"
#       of the book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    - A utility that can take N number of still images from a streaming
#      video in a specified time frame.
#    - See 'Running the program' section below for further information.
#
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
#   ffmpegcolorspace, capsfilter,
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
# *Running the program:
#   Run the program in the command console as:
#
#  $python ImagesFromVideo.py [options]
#
#   Where, the [options] are:
#
#   --input_file   : The full path to input video file from which one or more
#                    frames need to be captured and saved as images.
#   --start_time   : The position in seconds on the video track. This will
#                    be the starting position from which one or more
#                    video frames will be captured as still image(s)
#                    NOTE: THE FIRST SNAPSHOT WILL ALWAYS BE AT start_time
#   --duration     : The duration (in seconds) of the video track starting
#                    from the "start_time". N number of frames will be captured
#                    starting from start time.
#   --num_of_captures: Total number of frames that need to be captured from
#                     start_time (including it) up to ,
#                     end_time= start_time + duration
#                    ( but not including the still image at end_time)
#                      NOTE: THE FIRST SNAPSHOT WILL ALWAYS BE AT start_time.
#                      so there won't be any snapshot at the end_time.You
#                      can extend this application (minor changes required)
#                      so that it also captures image at end_time
#
#    Example: Suppose you want to save 10 video frames as images, from
#    40 second to 42 seconds on the video time-line. This utility
#    will save 10 still images starting at 40 seconds,  saving image
#    after every 0.2 seconds. STARTING AT 40.0 second
#    i.e. (540.0, 40.2, 40.4 ... up to 42 seconds)
#
#   The still images will be saved in a newly created directory
#   'STILL_IMAGES' within the input directory. (Make sure you have write
#   permission in the input directory)
#
#-------------------------------------------------------------------------------

import os, sys, time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst
from optparse import OptionParser


class ImageCapture:
    """
    A utility that can take N number of still images from
    a streaming video in a specified time frame.
    Example: Suppose you want to save 10 video frames as images, from
    40 second to 42 seconds on the video time-line. This utility
    will save 10 still images starting at 40 seconds,  saving image
    after every 0.2 seconds. (40.2, 40.4 ... up to 42 seconds)
    """
    def __init__(self):
        self.is_playing = False
        # Flag used for printing purpose only.
        self.error_msg = ''

        #Flag used for printing purpose only.
        self.error_msg = ''
        self.deltaTime = None
        self.inFileLocation = ''

        self.processArgs()

        # Note that self.media_duration is in nano seconds.
        self.deltaTime = int(self.media_duration / self.numberOfCaptures)

        dir, fil = os.path.split(self.inFileLocation)
        pth = os.path.join(dir , 'STILL_IMAGES')
        if not os.path.exists(pth):
            os.makedirs(pth)

        self.outputDirPath = pth

        self.constructPipeline()
        self.connectSignals()

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # capture the messages put on the bus.
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # gnlsource plugin uses dynamic pads.
        # Capture the pad_added signal.
        self.gnlfilesrc.connect("pad-added",
                             self.gnonlin_pad_added)

    def constructPipeline(self):
        """
        Create the pipeline, add and link elements.
        """
        self.pipeline = gst.Pipeline()
        self.gnlfilesrc = \
        gst.element_factory_make("gnlfilesource")

        # Set properties of filesrc element
        # Note: the gnlfilesource signal will be connected
        # in self.connectSignals()
        self.gnlfilesrc.set_property("uri",
                                  "file:///" + self.inFileLocation)

        self.colorSpace = gst.element_factory_make("ffmpegcolorspace")

        self.encoder= gst.element_factory_make("ffenc_png")

        self.filesink = gst.element_factory_make("filesink")

        self.pipeline.add(self.gnlfilesrc,
                          self.colorSpace,
                          self.encoder,
                          self.filesink)
        gst.element_link_many(self.colorSpace,
                          self.encoder,
                          self.filesink)

    def gnonlin_pad_added(self, gnonlin_elem, pad):
        """
        Capture the pad_added signal to manually
        link gnlfilesrc pad with the queue1 and queue2
        """
        compatible_pad = None
        caps = pad.get_caps()
        name = caps[0].get_name()
        if name[:5] == 'video':
            compatible_pad = self.colorSpace.get_compatible_pad(pad, caps)

        if compatible_pad:
            pad.link(compatible_pad)

    def captureImage(self):
        """
        Capture the N number of still images from the
        streaming video.
        @see: self.capture_single_image()
        """
        # Record start time
        starttime = time.clock()

        # Note: all times are in nano-seconds
        media_end = self.media_start_time + self.media_duration
        start = self.media_start_time
        while start < media_end:
            self.capture_single_image(start)
            start += self.deltaTime

        endtime = time.clock()
        self.printFinalStatus(starttime, endtime)

        evt_loop.quit()

    def capture_single_image(self, media_start_time):
        """
        Save a single still image starting at 'media_start_time'
        Note that the duration is set to a very small value,
        0.01 seconds.
        """
        # Set media_duration as int as
        # gnlfilesrc takes it as integer argument
        media_duration = int(0.01*gst.SECOND)

        self.gnlfilesrc.set_property("media-start",
                                  media_start_time)
        self.gnlfilesrc.set_property("media-duration",
                                     media_duration)

        # time stamp in seconds, added to the name of still image
        # to be saved.
        time_stamp = 1.0*media_start_time/gst.SECOND
        outFile = os.path.join(self.outputDirPath,
                               "still_%.4f.png"%time_stamp )
        print "\n outfile = ", outFile
        self.filesink.set_property("location", outFile)
        self.is_playing = True
        self.pipeline.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False
            self.error_msg = message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False

    def processArgs(self):

        """
        Process the command line arguments.
        """
        parser = OptionParser(usage=self.printUsage())
        parser.add_option("-s", "--start_time",
                          dest="start_time",
                          default=0.0,
                          type=float,
                          help="Start time in seconds")
        parser.add_option("-d", "--duration",
                          dest="duration",
                          default=1.0,
                          type=float,
                          help="End time in seconds")
        parser.add_option("-i", "--input_file",
                          dest="inFileLocation",
                          default="",
                          help="Input File Path")
        parser.add_option("-n", "--num_of_captures",
                          dest="numOfCaptures",
                          default=1,
                          type=int,
                          help="Number of still image captures")

        (options, args) = parser.parse_args()

        # convert all the times in nano-seconds.
        # These need to be of type ineger as these will be set as
        # properties for gnlfilesource element.
        self.media_start_time = int((options.start_time)*gst.SECOND)
        self.media_duration = int((options.duration)*gst.SECOND)
        self.numberOfCaptures = options.numOfCaptures

        if not options.inFileLocation:
            print " \n Exiting program. You must specify input file"
            sys.exit(2)

        self.inFileLocation = os.path.normpath(options.inFileLocation)

    def printUsage(self):
        usage = "***Program to capture still images from a video***"\
        "\n The [options] are:"\
        "\n--input_file     : The full path to input video file from which one or "\
        "more frames need to be captured and saved as images."\
        "\n--start_time     : The position in seconds on the video track. "\
        " This will be the starting position from which one or more  video "\
        "frames will be captured"\
        "/n NOTE: THE FIRST SNAPSHOT WILL ALWAYS BE AT start_time"\
        "\n--duration       : The duration (in seconds) of the video track starting"\
        " from the start_time. N number of frames will be captured."\
        "\n--num_of_captures: Total number of frames that need to be captured from"\
        "start_time (including it) up to , end_time= start_time + duration"\
        "( but not including the still image at end_time)"
        return usage

    def printFinalStatus(self, starttime, endtime):
        """
        Print the final status message.
        """

        if self.error_msg:
            print self.error_msg
        else:
            print "\n Done!"
            print "\n Still images saved to %s" %(self.outputDirPath)
            print "\n Approximate time required :  \
            %.4f seconds" % (endtime - starttime)

# Run the program
imgCapture = ImageCapture()
thread.start_new_thread(imgCapture.captureImage, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()



