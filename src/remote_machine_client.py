import argparse


import Pyro4

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--func_name", type=str, required=True, help="name of the funtion to be run")
ap.add_argument("-n", "--name", type=str, required=True, help="the name of the widget")
ap.add_argument("-x", "--xpos", type=int, help="x coordinate of the new position")
ap.add_argument("-y", "--ypos", type=int, help="y coordinate of the new position")
ap.add_argument("-w", "--width", type=int, help="new width of the widget")
ap.add_argument("-ht", "--height", type=int, help="new height of the widget")


args = vars(ap.parse_args())


function_name = args["func_name"]
screen = Pyro4.Proxy("PYRONAME:videowall_agent_1")  # bu ekranı temsil ediyor.


def move_to(args):
    name = args["name"]
    xpos = args["xpos"]
    ypos = args["ypos"]
    screen.move_widget(name=name, xpos=xpos, ypos=ypos)


def resize(args):
    name = args["name"]
    width = args["width"]
    height = args["height"]
    screen.move_widget(name=name, width=width, height=height)


locals()[function_name](args)

# wall.message("Hello there!")
# wall.message("How is it going?!")
# wall.add_image()

print("done!")
