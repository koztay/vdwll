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
#    -  This file, SingleImageAnimation.py is an example that shows how to move
#       and rotate a single image to create the animation effect. Here a
#      ball is shown bouncing up and down, This uses python and Pyglet.
#    -   It is created as an illustration for Chapter 4 section ,
#        'Single Image Animation' of the book:
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
#  Put this file in a directory and place the image file, ball.png in a
#  subdirectory called  'images'
#
#  $python SingleImageAnimation.py
#
#  This will show the animation in a pyglet window.
#-------------------------------------------------------------------------------

import pyglet
import time

class SingleImageAnimation(pyglet.window.Window):
    def __init__(self, width = None, height = None):
        pyglet.window.Window.__init__(self,
                                      width = width,
                                      height = height,
                                      resizable = True)
        self.drawableObjects = []
        self.rising = False
        self.ballSprite = None
        self.paused = False
        self.createDrawableObjects()
        self.adjustWindowSize()

    def createDrawableObjects(self):
        """
        Create sprite objects that will be drawn within the
        window.
        """
        ball_img= pyglet.image.load('images/ball.png')
        ball_img.anchor_x = ball_img.width / 2
        ball_img.anchor_y = ball_img.height / 2

        self.ballSprite = pyglet.sprite.Sprite(ball_img)
        self.ballSprite.position = (self.ballSprite.width + 100,
                                     self.ballSprite.height*2 - 50)

        self.drawableObjects.append(self.ballSprite)

    def adjustWindowSize(self):
        """
        Resizes the pyglet window.
        """
        w = self.ballSprite.width*3
        h = self.ballSprite.height*3
        self.width = w
        self.height = h

    def on_draw(self):
        """
        Overrides pyglet.window.Window.on_draw to draw the sprite.
        """
        self.clear()
        for d in self.drawableObjects:
            d.draw()

    def on_key_press(self, key, modifiers):
        """
        Overrides pyglet.window.Window.on_key_press to handle
        key presee event
        """
        if key == pyglet.window.key.P and not self.paused:
            pyglet.clock.unschedule(self.moveObjects)
            self.paused = True
        elif key == pyglet.window.key.R and self.paused:
            pyglet.clock.schedule_interval(win.moveObjects, 1.0/20)
            self.paused = False

    def moveObjects(self, t):
        """
        Move the image sprites / play the sound .
        This method is scheduled to be called every 1/N seconds using
        pyglet.clock.schedule_interval.
        """
        if self.ballSprite.y - 100 < 0:
            self.rising = True
        elif self.ballSprite.y > self.ballSprite.height*2 - 50:
            self.rising = False

        if not self.rising:
            self.ballSprite.y -= 5
            self.ballSprite.rotation -= 6
        else:
            self.ballSprite.y += 5
            self.ballSprite.rotation += 5

win = SingleImageAnimation()

# Set window background color to white.
r, g, b, alpha = 1, 1, 1, 1
pyglet.gl.glClearColor(r, g, b, alpha)

# Schedule the method win.moveObjects to be called every
# 0.05 seconds.
pyglet.clock.schedule_interval(win.moveObjects, 1.0/20)


pyglet.app.run()



