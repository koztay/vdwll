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
#    -  This file, BowlingAnimation.py is an example that shows how to create
#      an animation by modifying the position of the images. It uses
#      Python and Pyglet to accomplish this. This example also illustrates
#      how to add mouse controls to an animation.
#
#    -   It is created as an illustration for Chapter 4 section ,
#        'Project: A Simple Bowling Animation' of the book:
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
#  Then put the image files ball.png and pin.png in the 'images' directory
#  and run the program as:
#
#  $python BowlingAnimation.py
#
#  This will show the animation in a pyglet window.
#  Press 'P'  key on the keyboard to pause the animation.
#  To resume a paused animation, press the 'R' key.
#-------------------------------------------------------------------------------

import pyglet
import time

class BowlingAnimation(pyglet.window.Window):
    def __init__(self, width = None, height = None):
        pyglet.window.Window.__init__(self, width = width, height = height)
        self.drawableObjects = []
        self.paused = False
        self.ballSprite = None
        self.pinHorizontal = False
        self.createDrawableObjects()
        self.adjustWindowSize()

    def createDrawableObjects(self):
        """
        Create the objects (sprites) for drawing within the
        pyglet Window.
        """
        ball_img= pyglet.image.load('images/ball.png')
        ball_img.anchor_x = ball_img.width / 2
        ball_img.anchor_y = ball_img.height / 2

        pin_img = pyglet.image.load('images/pin.png')
        pin_img.anchor_x = pin_img.width / 2
        pin_img.anchor_y = pin_img.height / 2

        self.ballSprite = pyglet.sprite.Sprite(ball_img)
        self.ballSprite.position = (0 + 100,
                                     self.ballSprite.height)

        self.pinSprite = pyglet.sprite.Sprite(pin_img)
        self.pinSprite.position = (self.ballSprite.width*2 + 100,
                                     self.ballSprite.height)

        # Add these sprites to the list of drawables
        self.drawableObjects.append(self.ballSprite)
        self.drawableObjects.append(self.pinSprite)

    def adjustWindowSize(self):
        """
        Adjust the width and height of the Pyglet Window.
        """
        w = self.ballSprite.width*3 + 100
        h = self.ballSprite.height*2
        self.width = w
        self.height = h

    def on_draw(self):
        """
        The overridden API method on_draw which is called when the Window
        needs to be re-drawn.
        """
        self.clear()
        for d in self.drawableObjects:
            d.draw()

    def on_key_press(self, key, modifiers):
        """
        Captures key press events.
        Overrides pyglet.window.Window.on_key_press()
        """
        if key == pyglet.window.key.P and not self.paused:
            pyglet.clock.unschedule(self.moveObjects)
            self.paused = True
        elif key == pyglet.window.key.R and self.paused:
            pyglet.clock.schedule_interval(self.moveObjects, 1.0/20)
            self.paused = False

    def moveObjects(self, t):
        """
        Translate and rotate the sprites to accomplish
        the animation effect. This method is called by
        pyglet.clock.moveObjects every 1/20 seconds.
        @arg t: The current time.
        """
        if self.pinHorizontal:
            self.ballSprite.x = 100
            self.pinSprite.x -= 100

        if self.ballSprite.x < self.ballSprite.width*2:
            if self.ballSprite.x == 100:
                time.sleep(1)
                self.pinSprite.rotation = 0
                self.pinHorizontal = False

            self.ballSprite.x += 5
            self.ballSprite.rotation += 5

        if self.ballSprite.x >= self.ballSprite.width*2:
            self.pinSprite.rotation = 90
            self.pinSprite.x += 100
            self.pinHorizontal = True


# Create a Pyglet Window instance to show the animation.
win = BowlingAnimation()

# Set window background color to white.
r, g, b, alpha = 1, 1, 1, 1
pyglet.gl.glClearColor(r, g, b, alpha)

# Schedule the method BowlingAnimation.moveObjects to be called every
# 0.05 seconds.

pyglet.clock.schedule_interval(win.moveObjects, 1.0/20)

pyglet.app.run()