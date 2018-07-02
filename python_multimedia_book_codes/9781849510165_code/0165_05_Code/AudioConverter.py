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
#    -  This file, AudioConverter.py defines a class AudioConverter.
#       It takes the input audio files and saves them with
#       a user specified audio file format (creates new audio files).
#       This is created as an illustration for Chapter 5 section
#       "Converting Audio File Formats"  of the book:
#       "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#-------------
# Details
#-------------
#    This tool takes one or more input audio files, and convert those into a user
#    user specified audio file format. For each input file, a new file is
#    created provided that a different file location is specified using the
#    --output_dir  option.
#     The program can be run as :
#          $python AudioFileConverter.py  [options]
#
# Where, the [options] are as follows:
#  --input_dir   : The directory from which to read the input audio file(s) to
#                  be converted
#  --input_format: The audio format of the input files. The format should be
#                  in a supported list of formats. The supported formats are
#                  "mp3", "ogg"  and  "wav". If no format is specified,
#                  it will use the default format as ".wav" .See a TODO item
#                  for a possible extension of this utility.
# --output_dir   : The output directory where the converted files will be saved
# --output_format: The audio format of the output file. Supported output formats
#                  are "wav" and "mp3"
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
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
# @TODO:
#       1. Extend this application to support more audio output formats like ogg,
#          flac. One of the simplest thing to do is to define proper elements
#          (such as encoder and muxer) and instead of constructing a pipeline
#          from individual elements, use gst.parse_launch method and let it
#          automatically create and link elements using the command string.
#       2. The audio converter illustrated in this example takes input files of
#          only a single audio file format. This can easily be extended to
#          accept input audio files in all supported file formats (except for
#          the type specified by the --output_format option. The decodebin
#          should take care of decoding the given input data. Extend this
#          application to support this feature. You will need to modify the code
#          in AudioConverter.convert() method
#-------------------------------------------------------------------------------

import os, sys, time
import thread
import getopt, glob
import gobject
import pygst
pygst.require("0.10")
import gst


def audioFileExists(fil):
    """
    Returns whether the given file 'fil' exists.
    @see: AudioConverter.convert() .. the caller to this function.
    """
    return os.path.isfile(fil)

class AudioConverter:
    """
    A simple audio converter that takes one or more input audio files and saves
    them with  a user specified audio file format (creates new audio files)
    """
    def __init__(self):
        # Initialize various attrs
        self.inputDir = os.getcwd()
        self.inputFormat = "wav"
        self.outputDir = ""
        self.outputFormat = ""
        self.error_message = ""

        self.encoders = {"mp3":"lame",
                  "wav": "wavenc"}

        self.supportedOutputFormats = self.encoders.keys()

        self.supportedInputFormats = ("ogg", "mp3", "wav")

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
        self.decodebin = gst.element_factory_make("decodebin")
        self.audioconvert = gst.element_factory_make("audioconvert")
        self.filesink = gst.element_factory_make("filesink")
        encoder_str =  self.encoders[self.outputFormat]
        self.encoder= gst.element_factory_make(encoder_str)

        self.pipeline.add( self.filesrc, self.decodebin,
                           self.audioconvert, self.encoder,
                           self.filesink)

        gst.element_link_many(self.filesrc, self.decodebin)
        gst.element_link_many(self.audioconvert, self.encoder, self.filesink)

    def connectSignals(self):
        """
        Connect various signals with the class methods.
        """
        # Connect the signals. ( catch the messages on the bus )
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect the decodebin "pad_added" signal.
        self.decodebin.connect("pad_added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        audioconvert, when the decodebin element generated "pad_added" signal
        """
        caps = pad.get_caps()
        compatible_pad = self.audioconvert.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

    def processArgs(self):
        """
        Process the command line arguments. Print error and the usage
        if there is an error processing the user supplied arguments.
        """
        # Process command line arguments
        args = sys.argv[1:]
        shortopts = ''
        longopts = ['input_dir=', 'input_format=',
                    'output_dir=', 'output_format=' ]
        try:
            opts, args = getopt.getopt(args, shortopts, longopts)
        except getopt.GetoptError, error:
            # print usage
            self.printUsage()
            # print the error message and exit.
            sys.exit(error)

        if not len(opts):
            self.printUsage()
            sys.exit(2)

        for opt, val in opts:
            print opt
            if opt == "--input_dir":
                assert os.path.exists(val)
                self.inputDir = os.path.normpath(val)
            elif opt == "--output_dir":
                assert os.path.exists(val)
                self.outputDir = os.path.normpath(val)
            elif opt == "--input_format":
                format = val
                format = format.lower()
                assert format in self.supportedInputFormats
                self.inputFormat = val
            elif opt == "--output_format":
                format = val
                format = format.lower()
                assert format in self.supportedOutputFormats
                self.outputFormat = val

        #Now check if output directory has been specified. If not, create one.
        if not self.outputDir:
            pth = os.path.join(self.inputDir , 'OUTPUT_AUDIOS')
            if not os.path.exists(pth):
                os.makedirs(pth)
            self.outputDir = pth

        if not self.outputFormat:
            print ("\n Output audio format not specified."
            "Saving audio file in the default \"mp3\" format.")
            self.outputFormat = "mp3"


    def printUsage(self):
        print "\n Audio converter usage:"
        print "\n python AudioConverter [options]"
        print "\n The [options] are:"
        print (" \n"
        "--input_dir   : The directory from which to read the input audio file(s) to " 
        "\nbe converted" 
        "\n--input_format: The audio format of the input files. The format should be "
        "\n in a supported list of formats. The supported formats are "
        "\n \"mp3\", \"ogg\" and  \"wav\". If no format is specified, "
        "\n it will use the default format as \".wav\" ."
        "\n --output_dir   : The output directory where the converted files will be saved "
        "\n --output_format: The audio format of the output file. Should be in the "
        "\n  supported formats are \"wav\" and \"mp3\". If no format is specified, "
        "\n it will use \"mp3\" as the default output format")

    def printFinalStatus(self, inputFileList, starttime, endtime):
        """
        Print the final status of audio conversion process.
        """
        if self.error_message:
            print self.error_message
        else:
            print "\n Done!"
            print ("\n  %d audio(s) written to directory:"
            "%s")%(len(inputFileList), self.outputDir)
            print ("\n Approximate time required for conversion:"
            "%.4f seconds") % (endtime - starttime)

    def convert(self):
        """
        Convert the input audio files into user specified audio format.
        @see: self.convert_single_audio()
        """
        pattern = "*." + self.inputFormat
        filetype = os.path.join(self.inputDir, pattern)
        fileList = glob.glob(filetype)
        inputFileList = filter(audioFileExists, fileList)

        if not len(inputFileList):
            print ("\n No audio files with extension %s located"
            "in dir %s")%(self.outputFormat, self.inputDir)
            return
        else:
            # Record time before beginning audio conversion
            starttime = time.clock()
            print "\n Converting Audio files.."

        # Save the audio into specified file format.
        # Do it in a for loop
        # If the audio by that name already
        # exists, do not overwrite it OR define and use
        # flag -f to decide whether to overwrite it!
        for inPath in inputFileList:
            dir, fil = os.path.split(inPath)
            fil, ext = os.path.splitext(fil)
            outPath = os.path.join(self.outputDir,
                                   fil + "." + self.outputFormat)
            # Following check is already done.
            #if not self.encoders.has_key(ext):
                #print " Invalid extension ", ext


            print "\n Input File: %s%s, Conversion STARTED..." % (fil, ext)
            self.convert_single_audio(inPath, outPath)
            if self.error_message:
                print "\n Input File: %s%s, ERROR OCCURED." % (fil, ext)
                print self.error_message
            else:
                print "\n Input File: %s%s, Conversion COMPLETE " % (fil, ext)

        endtime = time.clock()

        self.printFinalStatus(inputFileList, starttime, endtime)
        evt_loop.quit()

    def convert_single_audio(self, inPath, outPath):
        """
        Convert a single audio file and save it.
        @param inPath: Input audio file path
        @type inPath: string
        @param outPath: Output audio file path
        @type outPath: string
        """
        # @NOTE: The following applies mainly for Windows platform.
        # The inPath is obtained from the 'for loop'. The os.path.normpath
        # doesn't work on this string. GStreamer will throw error processing
        # such path
        # One way to handle this is to use repr(string) , which will return the
        # whole string including the quotes .
        # For example: if inPath = "C:/AudioFiles/my_music.mp3"
        # repr(inPath) will return "'C:\\\\AudioFiles\\\\my_music.mp3'"
        # We will need to get rid of the extra single quotes at the beginning
        # and end by slicing the string as  inPth[1:-1]
        inPth = repr(inPath)
        outPth = repr(outPath)

        # Set the location property for file source and sink
        self.filesrc.set_property("location", inPth[1:-1])
        self.filesink.set_property("location", outPth[1:-1])

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
            self.error_message = message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            self.is_playing = False

# Run the converter
converter = AudioConverter()
thread.start_new_thread(converter.convert, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()
