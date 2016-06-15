# @author Drew McCoy <drewm@alleninstitute.org>
# Testing circle/rect idea

from psychopy import visual, core, event


class Skeleton:

    def __init__(self, window, vertices):
        self.vertices = vertices
        self.length = len(vertices)
        self.skeleton = visual.ShapeStim(win=window,
                                        vertices=self.vertices,
                                        closeShape=False
                                        )
        self.shapeList = []
        self._createShapeList(window=window)

    def draw(self):
        for i in range(len(self.shapeList)):
            self.shapeList[i].draw()

    def _createShapeList(self, window):
        if self.length > 0:
            # create first circle and add (fence post)
            circle = visual.Circle(win=window,
                                    radius = 0.5,
                                    edges = 32,
                                    fillColor = "white",
                                    pos = self.vertices[0]
                                    )
            self.shapeList.append(circle)

            # add rest of the 'fence'
            vertex = 1
            while vertex < self.length:
                # draw rectangle

                # create end circle
                circleEnd = visual.Circle(win=window,
                                        radius = 0.5,
                                        edges = 32,
                                        fillColor = "white",
                                        pos = self.vertices[vertex]
                                        )
                self.shapeList.append(circleEnd)
                vertex += 1
