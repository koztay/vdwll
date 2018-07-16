from __future__ import print_function
import time

import Pyro4

wall = Pyro4.Proxy("PYRONAME:videowall_agent")


wall.message("Hello there!")
wall.message("How is it going?!")
wall.add_image()


print("done!")


