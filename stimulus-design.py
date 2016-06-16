# @author Drew McCoy <drewm@alleninstitute.org>
# main script for stimulus design

# imports
from psychopy import visual, core, event
from shapes import Skeleton

# create a window
mywin = visual.Window([800,800],
                      monitor="testMonitor",
                      units="deg")

# a bunch of lists of vertices to test
v1 = [(-1, 1), # Z
      (1, 1),
      (-1, -1),
      (1, -1)]
v2 = [(-1, 1), # square
      (1, 1),
      (1, -1),
      (-1, -1),
      (-1, 1)]
v3 = [(1, 1),
      (-1, 1),
      (1, -2),
      (-1, -2)]

# Skeleton shape
skel = Skeleton(window=mywin,
                vertices=v3
                )

# -------------------------------------MAIN LOOP-----------------------------------------

# loop setup
play = True
frameN = 0

while play:

    # draw stims
    skel.draw()

    # if a key is pressed, set play to False
    if len(event.getKeys()) > 0:
        play = False
    event.clearEvents()

    # update window
    mywin.update()

    # increment frameN
    frameN += 1
# -----------------------------------END MAIN LOOP---------------------------------------

# cleanup
mywin.close()
core.quit()
