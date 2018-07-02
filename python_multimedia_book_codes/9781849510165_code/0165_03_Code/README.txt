README 

This folder contains:
1. The Images folder containing colored images used in Chapter 3
2. Code in file WaterMarkMaker.py
3. Supplementary material PDF for chapter 3
----------------------------------------------------

 Summary:
-------------
    -  This file, WaterMarkMaker.py is a Watermark Maker utility
       created for Chapter 3 Project of the book:
       "Python Multimedia Applications Beginners Guide"
       Publisher: Packt Publishing.
       ISBN: [978-1-847190-16-5]
    - The class WaterMarkMaker defined in this file
    - see WaterMarkMaker.py for more details. 

	
 Details:
------------
 This tool enables embedding a text, date stamp, and watermark to an
 input image. It can be run on the command line using the following syntax:

    $python WaterMarkMaker.py  [options]

Where, the [options] are as follows:
--image1 : The file path of the main image that provides canvas
--waterMark : The file path of the watermark image (if any)
--mark_pos : The coordinates of top left corner of the watermark image to be
             embedded. The values should be  specified in double quotes such
             as "100, 50"
--text : The text that should appear in the output image.
--text_pos : The coordinates of top left corner of the TEXT to be embedded.
             The values should be  specified in double quotes, such as "100,50"
--transparency : The transparency factor for the watermark (if any)
--dateStamp : Flag (True or False) that determines whether to insert date stamp
              in the image. If True, the date stamp at the time this image was
              processed will be insterted.

 EXAMPLE:
 -----------
 The following is an example that shows how to run this tool with all
 the options specified.

python WaterMarkMaker.py  --image1="C:\foo.png"
                          --watermark="C:\watermarkImage.png"
                          --mark_pos="200, 200"
                          --text="My Text"
                          --text_pos="10, 10"
                          --transparency=0.4
                          --dateStamp=True

 This creates an output image file WATERMARK.png, with a watermark and text at
 the specified anchor point within the image.