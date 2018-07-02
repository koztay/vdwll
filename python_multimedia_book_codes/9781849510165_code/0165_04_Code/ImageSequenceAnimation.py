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
#    -  This file, ImageSequenceAnimation.py is an example that shows how to
#      create an animation using a sequence of images, using python and Pyglet.
#    -   It is created as an illustration for Chapter 4 section ,
#        'Animation Using a Sequence of Images' of the book:
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
#  Put this file in a directory and place the image files clock1.png, clock2.png,
#  and clock3.png in the sub-directory called 'images'
#  Then run the program as:
#
#  $python ImageSequenceAnimation.py
#
#  This will show the animation in a pyglet window.
#-------------------------------------------------------------------------------

import pyglet

image_frames = ('images/clock1.png',
                'images/clock2.png',
                'images/clock3.png')

# Create the list of pyglet images
images = map(lambda img: pyglet.image.load(img), image_frames)

# Each of the image frames will be displayed for 0.33 seconds
# 0.33 seconds chosen so that the 'pendulam in the clock animation
# completes one oscillation in ~ 1 second !
animation = pyglet.image.Animation.from_image_sequence(images, 0.33)

# Create a sprite instance.
animSprite = pyglet.sprite.Sprite(animation)

# The main pyglet window with OpenGL context
w = animSprite.width
h = animSprite.height
win = pyglet.window.Window(width = w, height = h)

# Set window background color to white.
pyglet.gl.glClearColor(1, 1, 1, 1)

# The @win.event is a decorator that helps modify the API methods such as
# on_draw  called when draw event occurs.
@win.event
def on_draw():
    win.clear()
    animSprite.draw()

pyglet.app.run()

