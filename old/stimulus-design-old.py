# @author Drew McCoy <drewm@alleninstitute.org>
# main script for stimulus design
# OUTDATED

# imports
from psychopy import visual, core, event
from shapesold import SkeletonTemp, SkeletonNode, SkeletonStim

# create a window
mywin = visual.Window([800,800],
                      monitor="testMonitor",
                      units="deg")

# a bunch of lists of vertices to test
v1 = [(-100, 100), # Z
      (100, 100),
      (-100, -100),
      (100, -100)]
v2 = [(-100, 100), # square
      (100, 100),
      (100, -100),
      (-100, -100),
      (-100, 100)]
v3 = [(100, 100),  # vertical streched backwards Z
      (-100, 100),
      (100, -200),
      (-100, -200)]
v4 = [(-200, 100), # horizontal stretched Z
      (200, 100),
      (-200, -100),
      (200, -100)]

# SkeletonTemp testing
skelTemp = SkeletonTemp(window=mywin,
                vertices=v4
                )

# SkeletonStim testing
node4 = SkeletonNode(position=(0, 250))
node3 = SkeletonNode(position=(-100, 150), connections=[node4])
node2 = SkeletonNode(position=(100, 100), connections=[node3])
node1 = SkeletonNode(position=(0, 0), connections=[node2, node4])
node = SkeletonNode(position=(0, 0), connections=[node2])

skel1 = SkeletonStim(window=mywin, root=node3)
skel2 = SkeletonStim(window=mywin, root=node2)
skel3 = SkeletonStim(window=mywin, root=node)
skel4 = SkeletonStim(window=mywin, root=node1, thickness=10)

skel = skel4

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
