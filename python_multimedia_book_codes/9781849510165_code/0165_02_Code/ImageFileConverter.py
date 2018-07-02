#-------------------------------------------------------------------------------
# @author: Ninad Sathaye
# @copyright: 2009-2010, Ninad Sathaye email:ninad.consult@gmail.com.
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
#    -  is a an image converter utility created for Chapter 2
#      Heading "Reading and Writing Images" , of the
#       book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#    -  to run this, type
#      python ImageConverter.py [arguments] 
#
#    where, [arguments] are: 
#    --input_dir: The  directory path where the image files are located
#    --input_format : The format of the image files to be converted e.g. jpg
#    --output_dir: The location where you want to save the converted images. 
#    --output_format: The output image format e.g. jpg, png , bmp etc. 
#-------------------------------------------------------------------------------

import sys
import os
import Image
import getopt
import glob
import time


def imageFileExists(fil):
    """
    Returns whether the given file 'fil' exists.
    @see: ImageFileConverter.convertImage() .. the caller to this function.
    """
    return os.path.exists(fil)


class ImageFileConverter:
    """
    The ImageFileConverter class batch processes images
    """
    def __init__(self):
        self.inputDir = os.getcwd()
        self.inputFormat = "jpg"
        self.outputDir = ""
        self.outputFormat = ""
        self.supportedFormats = ('jpg', 'png', 'jpeg' , 'bmp', 'tiff')
        self.processArgs()
        self.convertImage()

    def processArgs(self):
        """
        Process the command line arguments. Print error and the usage
        if there is an error processing the user supplied arguments.
        """
        # Process command line arguments
        args = sys.argv[1:]
        shortopts = 'io:'
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

        for opt in opts:
            print opt
            if opt[0] == "--input_dir":
                assert os.path.exists(opt[1])
                self.inputDir = opt[1]
            elif opt[0] == "--output_dir":
                assert os.path.exists(opt[1])
                self.outputDir = opt[1]
            elif opt[0] == "--input_format":
                format = opt[1]
                format = format.lower()
                assert format in self.supportedFormats
                self.inputFormat = opt[1]
            elif opt[0] == "--output_format":
                format = opt[1]
                format = format.lower()
                assert format in self.supportedFormats
                self.outputFormat = opt[1]

        #Now check if output directory has been specified. If not, create one.
        if not self.outputDir:
            pth = os.path.join(self.inputDir , 'OUTPUT_IMAGES')
            if not os.path.exists(pth):
                os.makedirs(pth)
            self.outputDir = pth

        if not self.outputFormat:
            print ("\n Output image format not specified."
            "Saving images in the default \"jpg\" format.")
            self.outputFormat = "jpg"

    def printUsage(self):
        print ("\n Image File converter usage:"
               "\n python ImageFileConverter [options]"
               "\n The [options] are:"
               "\n --input_dir: The  directory path where the image files are located"
               "\n --input_format : The format of the image files to be converted e.g. jpg"
               "\n --output_dir: The location where you want to save the converted images. "
               "\n --output_format: The output image format e.g. jpg, png , bmp etc. ")
        

    def convertImage(self):
        pattern = "*." + self.inputFormat
        filetype = os.path.join(self.inputDir, pattern)
        fileList = glob.glob(filetype)
        inputFileList = filter(imageFileExists, fileList)

        if not len(inputFileList):
            print ("\n No image files with extension %s located "
            "in dir %s")%(self.outputFormat, self.inputDir)
            return
        else:
            # Record time before beginning image conversion
            starttime = time.clock()
            print "\n Converting images.."

        # Save image into specified file format. Do it in a for loop
        # If the image by that name already
        # exists, do not overwrite that image OR use flag -f to decide whether
        # to overwrite it.
        for imagePath in inputFileList:
            inputImage = Image.open(imagePath)
            dir, fil = os.path.split(imagePath)
            fil, ext = os.path.splitext(fil)
            outPath = os.path.join(self.outputDir,
                                   fil + "." + self.outputFormat)
            inputImage.save(outPath)

        endtime = time.clock()
        print "\n Done!"
        print ("\n  %d image(s) written to directory:"
        "%s") %(len(inputFileList), self.outputDir)
        print ("\n Approximate time required for conversion: "
        %.4f seconds") % (endtime - starttime)


ImageFileConverter()
