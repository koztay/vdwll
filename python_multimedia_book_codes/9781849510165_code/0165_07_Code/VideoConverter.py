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
#    -  This file, VideoConverter.py defines a class VideoConverter.
#       It takes an input Video file and saves it with
#       a user specified Video file format (creates a new Video file).
#       This is created as an illustration for Chapter 7 section
#       "Video Format Conversion"  of the book:
#       "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    This tool takes a video file as an input, and convert it into a user
#    user specified Video file format.
#
#     The program can be run as :
#          $python VideoFileConverter.py  [options]
#
# Where, the [options] are as follows:
#--input_path  : The full path of the video file we wish to convert.
#          The video format of the input files. The format should be in
#          a supported list of formats. The supported input formats  are
#          "mp4", "ogg", "avi" and "mov"
#--output_path : The full path of the output video file.  If not specified,
#          it will create a folder OUTPUT_VIDEOS  within the input directory
#          and save the file there with same name.
# --output_format: The audio format of the output file. Supported output
#          formats  are "ogg" and "mp4"
#
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
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
# @TODO:
#   Make this a batch processing utility.
#-------------------------------------------------------------------------------

import os, sys, time
import thread
import getopt, glob
import gobject
import pygst
pygst.require("0.10")
import gst

class VideoConverter:
    """
    A simple Video converter that takes an input Video file and saves
    it in a user specified Video file format (creates new Video file)
    """
    def __init__(self):
        # Initialize various attrs
        self.inFileLocation = ""
        self.outFileLocation = ""
        self.inputFormat = "ogg"
        self.outputFormat = ""
        self.error_message = ""
        # Create dictionary objects for
        # Audio / Video encoders for supported
        # file format
        self.audioEncoders = {"mp4":"lame",
                  "ogg": "vorbisenc"}

        self.videoEncoders={"mp4":"ffenc_mpeg4",
                  "ogg": "theoraenc"}

        self.muxers = {"mp4":"ffmux_mp4",
                       "ogg":"oggmux" }

        self.supportedOutputFormats = self.audioEncoders.keys()

        self.supportedInputFormats = ("ogg", "mp4", "avi", "mov")

        self.pipeline = None
        self.is_playing = False

        self.processArgs()
        self.constructPipeline()
        self.connectSignals()

    def constructPipeline(self):
        """
        Create an instance of gst.Pipeline, create, add element objects
        to this pipeline. Create appropriate connections between the elements.
        """
        self.pipeline = gst.Pipeline("pipeline")

        self.filesrc = gst.element_factory_make("filesrc")
        self.filesrc.set_property("location", self.inFileLocation)

        self.filesink = gst.element_factory_make("filesink")
        self.filesink.set_property("location", self.outFileLocation)

        self.decodebin = gst.element_factory_make("decodebin")
        self.audioconvert = gst.element_factory_make("audioconvert")

        audio_encoder =  self.audioEncoders[self.outputFormat]
        muxer_str =  self.muxers[self.outputFormat]
        video_encoder =  self.videoEncoders[self.outputFormat]

        self.audio_encoder= gst.element_factory_make(audio_encoder)
        self.muxer = gst.element_factory_make(muxer_str)
        self.video_encoder = gst.element_factory_make(video_encoder)

        self.queue1 = gst.element_factory_make("queue")
        self.queue2 = gst.element_factory_make("queue")
        self.queue3 = gst.element_factory_make("queue")

        self.pipeline.add( self.filesrc,
                           self.decodebin,
                           self.video_encoder,
                           self.muxer,
                           self.queue1,
                           self.queue2,
                           self.queue3,
                           self.audioconvert,
                           self.audio_encoder,
                           self.filesink)

        gst.element_link_many(self.filesrc, self.decodebin)

        gst.element_link_many(self.queue1, self.video_encoder,
                              self.muxer, self.filesink)

        gst.element_link_many(self.queue2, self.audioconvert,
                               self.audio_encoder, self.queue3,
                               self.muxer)

    def connectSignals(self):
        """
        Connect various signals with the class methods.
        """
        # Connect the signals. ( catch the messages on the bus )
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect the decodebin "pad_added" signal.
        self.decodebin.connect("pad-added", self.decodebin_pad_added)

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

    def processArgs(self):
        """
        Process the command line arguments. Print error and the usage
        if there is an error processing the user supplied arguments.
        """
        # Process command line arguments
        args = sys.argv[1:]
        shortopts = ''
        longopts = ['input_path=', 'output_path=', 'output_format=' ]
        try:
            opts, args = getopt.getopt(args, shortopts, longopts)
        except getopt.GetoptError, error:
            # print usagel
            self.printUsage()
            # print the error message and exit.
            sys.exit(error)

        if not len(opts):
            self.printUsage()
            sys.exit(2)

        for opt, val in opts:
            print opt
            if opt == "--input_path":
                assert os.path.exists(val)
                self.inFileLocation = os.path.normpath(val)
            elif opt == "--output_path":
                assert os.path.exists(val)
                self.outFileLocation = os.path.normpath(val)
            elif opt == "--output_format":
                format = val
                format = format.lower()
                assert format in self.supportedOutputFormats
                self.outputFormat = val

        dir, fil = os.path.split(self.inFileLocation)
        fil, ext = os.path.splitext(fil)

        if not self.outFileLocation:
            dirpth = os.path.join(dir , 'OUTPUT_VIDEOS')
            self.outFileLocation = os.path.join(dirpth,
                                               fil + "." + self.outputFormat)
        ext = ext.lower()
        assert ext[1:] in self.supportedInputFormats

        if not self.outputFormat:
            print "\n Output video format not specified.\
            Saving video file in the default \"mp4\" format."
            self.outputFormat = "mp4"

    def printUsage(self):
        print "\n Video converter usage:"
        print "\n python VideoConverter [options]"
        print "\n The [options] are:"
        print " \n"\
        "--input_path  : The full path of input video file to be converted"\
        "\n The Video format should be in a supported list of formats."\
        " The supported formats are \"mp4\", \"ogg\",\"avi\" and \"mov\" "\
        "\n --output_path   : The output path where the converted file" \
        " will be saved "\
        "\n --output_format: The Video format of the output file. Should be in the "\
        "\n  supported formats are \"ogg\" and \"mp4\". If no format is specified, "
        "\n it will use \"mp4\" as the default output format"

    def printFinalStatus(self, starttime, endtime):
        """
        Print the final status of Video conversion process.
        """
        if self.error_message:
            print self.error_message
        else:
            print "\n Done!"
            print "\n Video written to %s" % (self.outFileLocation)
            print "\n Approximate time required for conversion:  \
            %.4f seconds" % (endtime - starttime)

    def convert(self):
        """
        Convert a single Video file and save it.
        """
        # Record time before beginning Video conversion
        starttime = time.clock()

        print "\n Converting Video file.."
        print "\n Input File: %s, Conversion STARTED..." % self.inFileLocation

        self.is_playing = True
        self.pipeline.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)

        if self.error_message:
            print "\n Input File: %s, ERROR OCCURED." % self.inFileLocation
            print self.error_message
        else:
            print "\n Input File: %s, Conversion COMPLETE " % self.inFileLocation

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
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False
            self.error_message = message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False

# Run the converter
converter = VideoConverter()
thread.start_new_thread(converter.convert, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()
