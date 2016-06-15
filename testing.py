# @author Drew McCoy <drewm@alleninstitute.org>
# testing psychopy

from psychopy import visual, core, event  # import some libraries from PsychoPy
from shapes import Skeleton

# create a window
mywin = visual.Window([800,800],
                        monitor="testMonitor",
                        units="deg")

# create some stimuli
# circle with grating
grating = visual.GratingStim(win=mywin,
                        mask="circle",
                        size=3, sf=3)

# a square
square = visual.ShapeStim(win=mywin,
                        vertices=[(-1, -1),
                                    (-1, 1),
                                    (1, 1),
                                    (1, -1)]
                        # vertices=((-1, -1),
                        #             (-1, 1),
                        #             (1, 1),
                        #             (1, -1))
                        )

# a Z
zShape = visual.ShapeStim(win=mywin,
                        vertices=((-1, 1),
                                    (1, 1),
                                    (-1, -1),
                                    (1, -1)),
                        closeShape=False
                        )

# a thick Z
zThickShape = visual.ShapeStim(win=mywin,
                        vertices=((-1, 1),
                                    (1, 1),
                                    (-1, -1),
                                    (1, -1)),
                        closeShape=False,
                        lineWidth=10
                        )

# an outline of a Z
# coloring is interesting here, fillColor=[0, 0, 255] parameter is off
zOutline = visual.ShapeStim(win=mywin,
                        vertices=((-10, 10),
                                    (10, 10),
                                    (10, 8),
                                    (-7, -8),
                                    (10, -8),
                                    (10, -10),
                                    (-10, -10),
                                    (-10, -8),
                                    (7, 8),
                                    (-10, 8)),
                        # fillColor=[0, 0, 255]
                        )

# Skeleton test
skel = Skeleton(window=mywin,
                vertices=[(-1, 1),
                            (1, 1),
                            (-1, -1),
                            (1, -1)]
                )


# loop setup
play = True
frameN = 0

# makes circle blink
while play:
    # advance phase by 0.05 of a cycle
    # grating.setPhase(1.05, '+')

    # draw blinking stims
    if frameN % 100 < 80:
        # grating.draw()
        # square.draw()
        # zShape.draw()
        # zThickShape.draw()
        # zOutline.draw()
        pass

    # draw non-blinking stims
    skel.draw()

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
