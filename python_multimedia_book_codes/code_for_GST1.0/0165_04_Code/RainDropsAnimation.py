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
#    -  This file, RainDropsAnimation.py is an example that shows how to create
#      an animation by using different regions of a single image. It uses
#      Python and Pyglet to accomplish this. This example also illustrates
#      how to add mouse controls to an animation.
#
#    -   It is created as an illustration for Chapter 4 section ,
#        'Animations Using Different Image Regions' of the book:
#       "Python Multimedia Applications Beginners Guide"
#       Publisher: Packt Publishing.
#       ISBN: [978-1-847190-16-5]
#
# Dependencies
#---------------
#  In order to run the program the following packages need to be installed and
#  appropriate environment variables need to be set (if it is not done by the
#  installer automatically.)
# 1. Python 2.6
# 2. Pyglet 1.1.4 or later for Python 2.6
#
# @Note:
#   You should have Python2.6 installed. The python executable
#   PATH should also be  specified as an environment variable , so that
#   "python" is a known command when run from command prompt.
#
# *Running the program:
#  Put this file in a directory and create a sub-directory 'images'
#  Then put the image file droplet.png in the 'images' directory
#  and run the program as:
#
#  $python RainDropsAnimation.py
#
#  This will show the animation in a pyglet window.
#-------------------------------------------------------------------------------

import pyglet
import time

class RainDropsAnimation(pyglet.window.Window):
    def __init__(self, width = None, height = None):
        pyglet.window.Window.__init__(self,
                                      width = width,
                                      height = height)
        self.drawableObjects = []
        self.createDrawableObjects()

    def createDrawableObjects(self):
        """
        Create the objects (sprites) for drawing within the
        pyglet Window.
        """
        num_rows = 4
        num_columns = 1
        droplet = 'images/droplet.png'
        animation = self.setup_animation(droplet,
                                         num_rows,
                                         num_columns)

        self.dropletSprite = pyglet.sprite.Sprite(animation)
        self.dropletSprite.position = (0,0)

        # Add these sprites to the list of drawables
        self.drawableObjects.append(self.dropletSprite)

    def setup_animation(self, img, num_rows, num_columns):
        """
        Create animation object using different regions of
        a single image.
        @param img: The image file path
        @type img: string
        @param num_rows: Number of rows in the image grid
        @type num_rows: int
        @param num_columns: Number of columns in the image grid
        @type num_columns: int
        """
        base_image = pyglet.image.load(img)
        animation_grid = pyglet.image.ImageGrid(base_image,
                                                num_rows,
                                                num_columns)
        image_frames = []

        for i in range(num_rows*num_columns, 0, -1):
            frame = animation_grid[i-1]
            animation_frame = pyglet.image.AnimationFrame(frame, 0.2)
            image_frames.append(animation_frame)

        animation = pyglet.image.Animation(image_frames)
        return animation

    def on_draw(self):
        """
        The overridden API method on_draw which is called when the Window
        needs to be re-drawn.
        """
        self.clear()
        for d in self.drawableObjects:
            d.draw()


# Create a Pyglet Window instance to show the animation.
win = RainDropsAnimation()

# Set window background color to white.
r, g, b, alpha = 1, 1, 1, 1
pyglet.gl.glClearColor(r, g, b, alpha)

pyglet.app.run()