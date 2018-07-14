# Centering Root Window on Screen

from tkinter import *

root = Tk()

# Gets the requested values of the height and widht.
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
print("Width", windowWidth, "Height", windowHeight)

# Gets both half the screen width/height and window width/height
# positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
# positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)
positionRight = int(4000)
positionDown = int(-600)

# Positions the window in the center of the page.
root.geometry("+{}+{}".format(positionRight, positionDown))

root.mainloop()
