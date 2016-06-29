# @author Drew McCoy <drewm@alleninstitute.org>
# main script for stimulus design

# imports
from psychopy import visual, core, event
from shapes import SkeletonNode, SkeletonStim, MotionStim

# create a window
mywin = visual.Window([800,800],
                      monitor="testMonitor",
                      units="deg")

# SkeletonStim testing
node4 = SkeletonNode(position=(0, 250))
node3 = SkeletonNode(position=(-100, 150), connections=[node4])
node2 = SkeletonNode(position=(100, 100), connections=[node3])
node1 = SkeletonNode(position=(0, 0), connections=[node2, node4])
node = SkeletonNode(position=(0, 0), connections=[node2])

skel1 = SkeletonStim(window=mywin, root=node3, stimulus_id=0)
skel2 = SkeletonStim(window=mywin, root=node2, stimulus_id=0)
skel3 = SkeletonStim(window=mywin, root=node, stimulus_id=0)
skel4 = SkeletonStim(window=mywin, root=node1, stimulus_id=0, thickness=10)

skel = skel4

dot = MotionStim(window=mywin,
                 n_dots=100,
                 coherence=.9,
                 field_size=(400, 200),
                 dot_size=2,
                 speed=5)

# -------------------------------------MAIN LOOP-----------------------------------------

# loop setup
play = True
frameN = 0

while play:

    # draw stims
    dot.draw()

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
