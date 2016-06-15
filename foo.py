from psychopy import visual, core, event

# create a window
mywin = visual.Window([800,800],
                        monitor="testMonitor",
                        units="deg")

# a circle
circle = visual.Circle(win=mywin,
                        radius = 0.5,
                        edges = 32,
                        fillColor = "white",
                        pos = (0,1)
                        )
# a rectangle
rectangle = visual.Rect(win = mywin,
                        width = 1,
                        height = 2,
                        fillColor = "white"
                        )


# loop setup
play = True
frameN = 0

# main execution loop
while play:

    # draw stims
    circle.draw()
    rectangle.draw()

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
