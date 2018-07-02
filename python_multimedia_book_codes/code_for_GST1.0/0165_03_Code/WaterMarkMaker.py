#-------------------------------------------------------------------------------
# @author: Ninad Sathaye
# @copyright: 2010, Ninad Sathaye email:ninad.consult@gmail.com.
# @license: GPL
# @summary:
#    -  This file, WaterMarkMaker.py is a Watermark Maker utility
#       created for Chapter 3 Project of the book:
#       "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#    - The class WaterMarkMaker defined in this file
#------------
# Details:
#------------
# This tool enables embedding a text, date stamp and watermark to an
# input image. It can be run on the command line using the following syntax:

#    $python WaterMarkMaker.py  [options]
#
#Where, the [options] are as follows:
#--image1 : The file path of the main image that provides canvas
#--waterMark : The file path of the watermark image (if any)
#--mark_pos : The coordinates of top left corner of the watermark image to be
#             embedded. The values should be  specified in double quotes such
#             as "100, 50"
#--text : The text that should appear in the output image.
#--text_pos : The coordinates of top left corner of the TEXT to be embedded.
#             The values should be  specified in double quotes, such as "100,50"
#--transparency : The transparency factor for the watermark (if any)
#--dateStamp : Flag (True or False) that determines whether to insert date stamp
#              in the image. If True, the date stamp at the time this image was
#              processed will be insterted.

# EXAMPLE:
# The following is an example that shows how to run this tool with all
# the options specified.
#
#python WaterMarkMaker.py  --image1="C:\foo.png"
#                          --watermark="C:\watermark.png"
#                          --mark_pos="200, 200"
#                          --text="My Text"
#                          --text_pos="10, 10"
#                          --transparency=0.4
#                          --dateStamp=True
#
# This creates an output image file WATERMARK.png, with a watermark and text at
# the specified anchor point within the image.

#-------------------------------------------------------------------------------

import Image, ImageDraw, ImageFont
import os, sys
import getopt
from datetime import date

class WaterMarkMaker:

    def __init__(self):
        # Image paths
        self.waterMarkPath = ''
        self.mainImgPath = ''
        # Text to be embedded
        self.text = ''
        # Transparency Factor
        self.t_factor = 0.5
        # Anchor point for embedded text
        self.text_pos = (0, 0)
        # Anchor point for watermark. Initialized as None
        # If it is not specified as an argument, the default value will
        # be computed later.
        self.mark_pos = None

        # Date stamp
        self.dateStamp = False
        # Image objects
        self.waterMark = None
        self.mainImage = None

        self.processArgs()
        self.createImageObjects()
        self.addText()
        self.addWaterMark()

        if self.dateStamp:
            self.addDateStamp()

        self.mainImage.save("C:\\images\\watermark.png")
        self.mainImage.show()

    def addWaterMark(self):
        """
        Process the water mark using the main image and the
        water mark image.
        """
        # There are more than one way to achieve
        # creating a watermark. The following flag,
        # if True will use Image.composite to create
        # the watermark.
        using_composite = False

        if self.waterMark is None:
            return
        # Add Transparency
        self.waterMark = self.addTransparency(self.waterMark)
        # Get the anchor point
        pos_x, pos_y = self._getMarkPosition(self.mainImage,
                                             self.waterMark)
        # Create the watermark
        if not using_composite:
            # Paste the image using the transparent
            # watermark image as the mask.
            self.mainImage.paste(self.waterMark,
                                 (pos_x, pos_y),
                                 self.waterMark)
        else:
            # Alternate method to create water mark.
            # using Image.composite.
            # Create a new canvas
            canvas = Image.new('RGBA',
                               self.mainImage.size,
                               (0,0,0,0))
            # Paste the watermark on the canvas
            canvas.paste(self.waterMark, (pos_x, pos_y))
            # Create a composite image
            self.mainImage = Image.composite(canvas,
                                             self.mainImage,
                                             canvas)


    def addText(self):
        """
        Prepare the text embedded in the main image.
        calls self._addTextWorker() for main processing.
        """
        if not self.text:
            return

        if self.mainImage is None:
            print "\n Main Image not defined."\
            "Returning."
            return

        txt = self.text
        self._addTextWorker(txt)

    def addDateStamp(self):
        """
        Add the date stamp to the image.
        @see: self._addTextWorker()
        """
        print "*** in addDateStamp"
        today = date.today()
        time_tpl = today.timetuple()
        year, month, day = time_tpl[0], time_tpl[1], time_tpl[2]
        datestamp = str(year) + "/" + str(month) + "/" + str(day)
        self._addTextWorker(datestamp, dateStamp = True)

    def _addTextWorker(self, txt, dateStamp = False):
        """
        This is the worker method that embeds the
        specified text in the main image.
        @param txt: the text to be embedded in the main image.
        @param dataStamp: The flag that decides where to insert
           the text. If True, the text is a date stamp, and so
           it will be inserted in the bottom left corner of the
           image. Otherwise the specified text position is used.
        @see: self.addText()
        """
        size = self.mainImage.size
        color = (0, 0, 0)
        textFont = ImageFont.truetype("arial.ttf", 50)

        # Create an ImageDraw instance to draw the text.
        imgDrawer = ImageDraw.Draw(self.mainImage)
        textSize = imgDrawer.textsize(txt, textFont)

        if dateStamp:
            pos_x = min(2, size[0])
            pos_y = size[1] - textSize[1]
            pos = (pos_x, pos_y)
        else:
            # We need to add text. Use self.text_pos
            pos = self.text_pos
        #finally add the text
        imgDrawer.text(pos, txt, font=textFont)

        if (textSize[0] > size[0] \
            or textSize[1] > size[1]):
            print "\n Warning, the specified text "\
               "going out of bounds."


    def addTransparency(self, img):
        """
        Modify the transparency level of the
        image.
        @param img: The img whose transparency
           needs to be modified
        """
        img = img.convert('RGBA')
        img_blender = Image.new('RGBA',
                                img.size,
                                (0,0,0,0))
        img = Image.blend(img_blender,
                          img,
                          self.t_factor)
        return img

    def createImageObjects(self):
        """
        Create instanced of Image class for the two input images.
        """
        self.mainImgPath = os.path.normpath(self.mainImgPath)
        self.mainImage = Image.open(self.mainImgPath)

        if self.waterMarkPath:
            self.waterMarkPath = os.path.normpath(self.waterMarkPath)
            self.waterMark = Image.open(self.waterMarkPath)

    def _getMarkPosition(self, canvasImage, markImage):
        """
        Return anchor point on the canvas which will be the
        top -left corner of the image to be embedded.
        @param canvasImage: The canvas image
        @type : Image
        @param markImage: The water mark or the text image.
        @type : Image
        @return return the position pixel coords(a 2-tuple.)
        """
        if self.mark_pos is not None:
            return self.mark_pos

        w_canvas, h_canvas = canvasImage.size
        w_mark, h_mark = markImage.size
        # Place the anchor point of the
        # image to be embedded near
        # bottom right corner.
        pos_x = w_canvas - w_mark
        pos_y = h_canvas - h_mark

        return (pos_x, pos_y)

    def processArgs(self):
        """
        Process the command line arguments. Print error and the usage
        if there is an error processing the user supplied arguments.
        """
        # Process command line arguments
        args = sys.argv[1:]
        shortopts = ''
        longopts = ['image1=', 'waterMark=', 'mark_pos=',
                    'text=', 'text_pos=', 'transparency=' ,
                    'dateStamp=' ]
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
            if opt == "--image1":
                assert os.path.exists(val)
                self.mainImgPath = val
            elif opt == "--waterMark":
                assert os.path.exists(val)
                self.waterMarkPath = val
            elif opt == "--text":
                assert val
                self.text = val
            elif opt == "--mark_pos":
                val = val.split(",")
                assert len(val) == 2
                self.mark_pos = (int(val[0]),
                            int(val[1]))
            elif opt == "--text_pos":
                val = val.split(",")
                assert len(val) == 2
                self.text_pos = (int(val[0]),
                            int(val[1]))
            elif opt == "--transparency":
                self.t_factor = float(val)
            elif opt == "--dateStamp":
                self.dateStamp = bool(val)
                print "*** dateStamp", self.dateStamp

        if not self.mainImgPath:
            self.printUsage()
            sys.exit(2)

    def printUsage(self):
        print "\n WaterMarkMaker usage: "\
        "\n python WaterMarkMaker.py [options]"\
        "\n The [options] are:"\
        "\n--image1 :The file path of the main image"\
        "            that provides canvas"\
        "\n--waterMark: The file path of the water mark"\
        "               image (if any)"\
        "\n--mark_pos: The coordinates of top left "\
        "              corner of the Watermark image."\
        "\n--text: The text that should appear in the output image."\
        "\n--text_pos: The coordinates of top left "\
        "              corner of the TEXT to be embedded."\
        "\n--transparency: The transparency factor for "\
        "                  the watermark (if any)"\
        "\n--dateStamp: Flag (True or False) that determines "\
        "               whether to insert date stamp in the image"\
        "\n\n **Example of how [options] can be specified**\n\n"\
        "\n --image1=\"C:\foo.py  "\
        "\n --waterMark=\"C:\wMark.png"\
        "\n --mark_pos=\"100,100\" "\
        "\n --text=\"My Image\" "\
        "\n --text_pos=\"100,100\" "\
        "\n --transparency=0.7"\
        "\n --dateStamp=True"

# Run the app
WaterMarkMaker()


