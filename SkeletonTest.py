# @author Drew McCoy <drewm@alleninstitute.org>
# Testing circle/rect idea

from psychopy import visual, core, event


class Skeleton:

    def __init__(self, window, vertices):
        self.vertices = vertices
        self.skeleton = visual.ShapeStim(win=window,
                                        vertices=self.vertices,
                                        closeShape=False
                                        )
        self._shapeList = []
        self._createShapeList(window=window)

    def draw(self):
        for i in range(len(self._shapeList)):
            self._shapeList[i].draw()

    def _createShapeList(self, window):
        if len(self.vertices) > 0:
            # create first circle and add (fence post)
            circle = visual.Circle(win=window,
                                    radius = 0.5,
                                    edges = 32,
                                    fillColor = "white",
                                    pos = self.vertices[0]
                                    )
            self._shapeList.append(circle)

            # add rest of the 'fence'
            vertex = 1
            while vertex < len(self.vertices):
                # draw rectangle

                # create end circle
                circleEnd = visual.Circle(win=window,
                                        radius = 0.5,
                                        edges = 32,
                                        fillColor = "white",
                                        pos = self.vertices[vertex]
                                        )
                self._shapeList.append(circleEnd)
                vertex += 1
