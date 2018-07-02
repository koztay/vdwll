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
#    -  This is a Thumbnail Maker utility created for Chapter 2 Project of the
#       book: "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#    - See 0165_2_ThumbnailMakerDialog.py for more details.
#    - The class ThumbnailMaker defined in this file is responsible
#      for main image processing. It defines various methods to accomplish this.
#      Example: _rotateImage, _makeThumbnail, _resizeImage
#      This class accepts input from ThumbnailMakerDialog. Thus, no Qt related
#      UI element/ method is required here. If you want to use some
#     other GUI framework to process input, just make sure to implement
#     the public API methods defined in class ThumbnailMakerDialog! (those are
#     used here.
#Other related file:
# - ThumbnailMakerDialog.py which defines UI related elements. This class
#   uses instance of ThumbnailMakerDialog to get required inputs.
#-------------------------------------------------------------------------------

import Image

class ThumbnailMaker:

    def __init__(self, dialog):
        """
        Constructor for class ThumbnailMaker.
        """
        # This dialog can be an instance of ThumbnailMakerDialog class
        # Alternatively, if you have some other way to process input,
        # it will be that class. Just make sure to implement the public
        # API methods defined in ThumbnailMakerDialog class!
        self._dialog = dialog

    def processImage(self):
        """
        Process the input arguments (specified through the
        Thumbnail Maker dialog). Based on these arguments the image
        will be resized (with given filter for resampling) and / or
        rotated by the given angle.
        If aspect ratio needs to be maintained, it calls _makeThumbnail method
        for resizing.
        @see: self._resizeImage()
        @see: self._makeThumbnail()
        @see: self._rotateImage()
        @see: ThumbnailMakerDialog._processImage() which calls this method.
        """

        filePath = self._dialog.getInputImagePath()

        imageFile = Image.open(filePath)

        if self._dialog.maintainAspectRatio:
            resizedImage = self._makeThumbnail(imageFile)
        else:
            resizedImage = self._resizeImage(imageFile)

        rotatedImage = self._rotateImage(resizedImage)

        fullPath = self._dialog.getOutImagePath()

        # Finally save the image.
        rotatedImage.save(fullPath)

    def _rotateImage(self, imageFile):
        """
        Rotate the image by the specified angle.
        """
        angle = self._dialog.getAngle()
        rotate = imageFile.rotate(angle)
        return rotate

    def _resizeImage(self, imageFile):
        """
        Resize the image to the specified size by applying the
        specified filter for image re-sampling.
        The size is a tuple (width, height) that specifies the new
        pixel dimensions of the image to be resized.
        @note: This method does NOT preserve the aspect ratio.
        The aspect ratio is preserved in self.makeThumbnail()
        """
        width, height = self._dialog.getSize()
        imageFilter = self._getImageFilter()
        resizedImage = imageFile.resize((width, height), imageFilter)
        return resizedImage

    def _makeThumbnail(self, imageFile):
        """
        Create a thumbnail or simply a resized image by maintaining
        aspect ratio of the image.
        @see: self.resizeImage() where the aspect ratio is not preserved.
        """
        foo = imageFile.copy()
        size = self._dialog.getSize()
        imageFilter = self._getImageFilter()
        foo.thumbnail(size, imageFilter)
        return foo

    def _getImageFilter(self):
        """
        Returns the specified image filter in the Thumbnail Maker dialog.
        This filter is used for image resampling.
        """
        imageFilterIndex = self._dialog.getImageFilterIndex()

        if imageFilterIndex == 0:
            imageFilter = Image.ANTIALIAS
        elif imageFilterIndex == 1:
            imageFilter = Image.BICUBIC
        elif imageFilterIndex == 2:
            imageFilter = Image.BILINEAR
        elif imageFilterIndex == 3:
            imageFilter = Image.NEAREST

        return imageFilter
