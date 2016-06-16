# @author Drew McCoy <drewm@alleninstitute.org>
# defines Rectangle, Skeleton

from psychopy import visual
import math

# class that defines a Rectangle ShapeStim, given two end points
class Rectangle:

    def __init__(self, window, p0, p1):
        self._rectangle = visual.Rect(win=window,
                                      fillColor="white",
                                      width=self._getWidth(p0, p1),
                                      height=self._getHeight(),
                                      pos=self._getPosition(p0, p1),
                                      ori=self._getOrientation(p0, p1)
                                      )
    def _getHeight(self):
        return 1

    def _getWidth(self, p0, p1):
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

    def _getPosition(self, p0, p1):
        # use midpoint formula
        print "(" + str(p0) + ", " + str(p1) + ")"
        x = (p1[0] + p0[0]) / 2
        y = (p1[1] + p0[1]) / 2
        print "(" + str(x) + ", " + str(y) + ")"
        return (x, y)

    def _getOrientation(self, p0, p1):
        # get change y and x
        dy = p1[1] - p0[1]
        dx = p1[0] - p0[0]

        # if slope is undefined
        if dx is 0:
            if dy < 0:
                return 45
            else:
                return 270

        # get slope
        slope = dy / dx

        # get temp radians of orientation (neg b/c psychopy is weird)
        rad = -math.atan(slope)

        # to degrees
        deg = math.degrees(rad)

        # if dy is neg, add 180
        if dy < 0:
            deg += 180

        return deg

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
                # if vertex is 1:
                rectangle = Rectangle(window=window,
                                      p0=self.vertices[vertex - 1],
                                      p1=self.vertices[vertex]
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
