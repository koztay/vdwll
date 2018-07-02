
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
#    -  This file, SimpleAnimation.py is an example that shows how to view
#      a GIF animation file using python and Pyglet.
#    -   It is created as an illustration for Chapter 4 section ,
#        'Viewing an Existing Animation' of the book:
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
#  Put this file in a direcotry and place the animation file SimpleAnimation.gif
#  in the sub-directory called 'images;
#  Then run the program as:
#
#  $python SimpleAnimation.py
#
#  This will show the animation in a pyglet window.  You can use
#  a different animation file instead of SimpleAnimation.gif. Just modify the
#  related code in this file OR add code to accept any gif file as a command line
#  argument for this program
#-------------------------------------------------------------------------------

import pyglet

animation = pyglet.image.load_animation("images/SimpleAnimation.gif")

# Create a sprite object as an instance of this animation.
animSprite = pyglet.sprite.Sprite(animation)

# The main pyglet window with OpenGL context
w = animSprite.width
h = animSprite.height
win = pyglet.window.Window(width = w, height = h)

# r,g b, color values and transparency for the background
r, g, b, alpha = 0.5, 0.5, 0.8, 1

# OpenGL method for setting the background.
pyglet.gl.glClearColor(r, g, b, alpha)

# Draw the sprite in the API methos on_draw of pyglet.Window
@win.event
def on_draw():
    """
    Draw the sprite in the API methos
    on_draw of pyglet.Window
    """
    win.clear()
    animSprite.draw()

pyglet.app.run()