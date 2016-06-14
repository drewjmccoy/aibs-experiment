# @author Drew McCoy <drewm@alleninstitute.org>
# testing psychopy

from psychopy import visual, core, event  # import some libraries from PsychoPy

# create a window
mywin = visual.Window([800,600],
                        monitor="testMonitor",
                        units="deg")

# create some stimuli
# circle with grating
grating = visual.GratingStim(win=mywin,
                        mask="circle",
                        size=3, sf=3)
# a square
square = visual.ShapeStim(win=mywin,
                        vertices=((-1, -1),
                                    (-1, 1),
                                    (1, 1),
                                    (1, -1))
                        )
# a Z
zShape = visual.ShapeStim(win=mywin,
                        vertices=((-1, 1),
                                    (1, 1),
                                    (-1, -1),
                                    (1, -1)),
                        closeShape=False
                        )

# loop setup
play = True
frameN = 0

# makes circle blink
while play:
    # advance phase by 0.05 of a cycle
    # grating.setPhase(1.05, '+')

    # draw stimuli half the time
    if frameN % 100 < 50:
        # grating.draw()
        # square.draw()
        zShape.draw()

    # if a key is pressed, set play to False
    if len(event.getKeys()) > 0:
        play = False
    event.clearEvents()

    # update window
    mywin.update()

    # increment frameN
    frameN += 1

# cleanup
mywin.close()
core.quit()
