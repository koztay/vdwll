README:

This folder contains:
1. The Images folder containing colored images used in Chapter 2, "Working with Images"
2. Code files used in the Chapter 2


*Prerequisites for the code:
See Chapter 2 , heading Installation Prerequisites 


1. File : 0165_2_ImageFileConverter.py: 
---------------------------------------

This batch processes files from a specified folder and saves 
these files with a user specified file format. 

This file can be run from the command line as:

python ImageConverter.py [arguments] 

where, [arguments] are: 
--input_dir: The  directory path where the image files are located
--input_format : The format of the image files to be converted e.g. jpg
--output_dir: The location where you want to save the converted images. 
--output_format: The output image format e.g. jpg, png , bmp etc. 



2. Files :

0165_2_thumbnailMaker.ui
0165_2_Ui_ThumbnailMakerDialog.py
0165_2_ThumbnailMakerDialog.py
0165_2_ThumbnailMaker.py
------------------------------------------

    This is a Thumbnail Maker utility created for Chapter 2 Project of the
    book: "Python Multimedia Applications Beginners Guide" ( Packt Publishing )
    ISBN: [978-1-847190-16-5]

    *Running the Application:
      This application can be run from command prompt as :
          $python  ThumbnailMakerDialog.py
      The following packages need to be installed on your machine
         - Python 2.6.4
         - PyQt v 4.6.2 ( for Python 2.6)
         - PIL  v 1.1.6 (for Python 2.6)
         - Refer to the book mentioned above for further details about
           other dependencies.
      This application is tested only on Windows XP.



