# @author Drew McCoy <drewm@alleninstitute.org>
# defines Skeleton

from psychopy import visual
import math

class Rectangle:

    def __init__(self, window, x, y):
        self._rectangle = visual.Rect(win=window,
                                      fillColor="white",
                                      width=self._getWidth(x, y),
                                      height=self._getHeight(),
                                      pos=(0,1),
                                      ori=self._getOrientation(x, y)
                                      )
    def _getHeight(self):
        return 1

    def _getWidth(self, x, y):
        return math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

    def _getOrientation(self, x, y):
        # TODO
        return 0

# draws a ShapeStim from a skeleton (list of verices)
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
                                   radius=0.5,
                                   edges=32,
                                   fillColor="white",
                                   pos=self.vertices[0]
                                   )
            self._shapeList.append(circle)

            # add rest of the 'fence'
            vertex = 1
            while vertex < len(self.vertices):
                # draw rectangle
                if vertex is 1:
                    rectangle = Rectangle(window=window,
                                          x=self.vertices[vertex - 1],
                                          y=self.vertices[vertex]
                                          )
                    self._shapeList.append(rectangle._rectangle)

                # create end circle
                circleEnd = visual.Circle(win=window,
                                          radius=0.5,
                                          edges=32,
                                          fillColor="white",
                                          pos=self.vertices[vertex]
                                          )
                self._shapeList.append(circleEnd)
                vertex += 1
