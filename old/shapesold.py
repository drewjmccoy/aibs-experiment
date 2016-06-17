# @author Drew McCoy <drewm@alleninstitute.org>
# defines Rectangle, Skeleton
# OUTDATED

from psychopy import visual
import math

# class that defines a Rectangle ShapeStim, given two end points
# Rectangle(window, p0, p1, thickness=20)
class Rectangle(object):

    # initializes the Rectangle
    def __init__(self, window, p0=(-100, 0), p1=(100, 0), thickness=20):
        self._rectangle = visual.Rect(win=window,
                                      units="pix",
                                      fillColor="white",
                                      width=self._getWidth(p0, p1),
                                      height=thickness,
                                      pos=self._getPosition(p0, p1),
                                      ori=self._getOrientation(p0, p1))

    def draw(self):
        self._rectangle.draw()

    # returns the width of the Rectangle
    def _getWidth(self, p0, p1):
        result = math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
        return result

    # returns the position (midpoint) of the Rectangle
    def _getPosition(self, p0, p1):
        # use midpoint formula
        x = (p1[0] + p0[0]) / 2
        y = (p1[1] + p0[1]) / 2
        return (x, y)

    # returns the orientation of the Rectangle in degrees. 0 is up, increasing
    # clockwise
    def _getOrientation(self, p0, p1):
        # get change y and x
        dy = p1[1] - p0[1]
        dx = p1[0] - p0[0]

        # if slope is undefined
        if dx is 0:
            if dy < 0:
                return 90
            else:
                return 270

        # get temp radians of orientation (neg b/c psychopy is weird)
        rad = -math.atan2(dy, dx)

        # to degrees
        deg = math.degrees(rad)

        return deg

# draws a ShapeStim from a skeleton (list of verices)
# SkeletonTemp(window, vertices, thickness)
class SkeletonTemp(object):

    def __init__(self, window, vertices=[], thickness=20):
        self.thickness = thickness
        self.vertices = vertices
        self.skeleton = visual.ShapeStim(win=window,
                                         units="pix",
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
                                   units="pix",
                                   radius=(self.thickness / 2),
                                   edges=32,
                                   fillColor="white",
                                   pos=self.vertices[0])
            self._shapeList.append(circle)

            # add rest of the 'fence'
            vertex = 1
            while vertex < len(self.vertices):

                # draw rectangle
                rectangle = Rectangle(window=window,
                                      p0=self.vertices[vertex - 1],
                                      p1=self.vertices[vertex])
                self._shapeList.append(rectangle._rectangle)

                # create end circle
                circleEnd = visual.Circle(win=window,
                                          units="pix",
                                          radius=(self.thickness / 2),
                                          edges=32,
                                          fillColor="white",
                                          pos=self.vertices[vertex])
                self._shapeList.append(circleEnd)
                vertex += 1

# a node of a skeleton data structure
# SkeletonNode(position, connections)
class SkeletonNode(object):

    # initializes node
    def __init__(self, position=(0, 0), connections=[]):
        self.position = position
        self.connections = connections

# a shape stimulus
# SkeletonStim(window, root, thickness)
class SkeletonStim(object):

    # initializes stimulus
    def __init__(self, window, root, thickness=20):
        self.window = window # window to be drawn on
        self.root = root # root SkeletonNode
        self.thickness = thickness # thickness of the lines

        # list of circles and rectangles that make up the shape
        self._shapeList = []

        # build up shape list
        self._buildShapeList(window=window)

    # draws the SkeletonStim on the window
    def draw(self):
        for i in range(len(self._shapeList)):
            self._shapeList[i].draw()

    # builds up the shape list with circles and squares
    def _buildShapeList(self, window):
        self._buildShapeListHelper(window, self.root)

    # helps build up shape list with recursion
    def _buildShapeListHelper(self, window, current):
        circle = visual.Circle(win=window,
                               units="pix",
                               radius=(self.thickness / 2),
                               edges=32,
                               fillColor="white",
                               pos=current.position)
        self._shapeList.append(circle)

        for i in range(len(current.connections)):
            rectangle = Rectangle(window=window,
                                  p0=current.position,
                                  p1=current.connections[i].position,
                                  thickness=self.thickness)
            self._shapeList.append(rectangle)
            self._buildShapeListHelper(window, current.connections[i])
