
from gi.repository import Gtk, Gdk

window = Gtk.Window()

# the screen contains all monitors
screen = Gdk.Screen.get_default()
print("screen size: %d x %d" % (screen.get_width(), screen.get_height()))

# collect data about each monitor
monitors = []
nmons = screen.get_n_monitors()
print("there are %d monitors" % nmons)
for m in range(nmons):
    mg = screen.get_monitor_geometry(m)
    print("monitor %d: %d x %d" % (m, mg.width, mg.height))
    monitors.append(mg)

# current monitor
curmon = screen.get_monitor_at_window(screen.get_monitor_at_window(window))
x, y, width, height = monitors[curmon]
print("monitor %d: %d x %d (current)" % (curmon, width, height))
