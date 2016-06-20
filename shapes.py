# @author Drew McCoy <drewm@alleninstitute.org>
# defines Rectangle, SkeletonNode, SkeletonStim

from psychopy import visual
import math

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

    # class that defines a Rectangle ShapeStim, given two end points
    # Rectangle(window, p0, p1, thickness=20)
    class _Rectangle(object):

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

    # initializes stimulus
    def __init__(self, window, root, shape_id, thickness=20):
        self.window = window # window to be drawn on
        self.root = root # root SkeletonNode
        self.id = shape_id # id of the
        self.thickness = thickness # thickness of the lines

        # list of circles and rectangles that make up the shape
        self._shape_list = []

        # build up shape list
        self._build_shape_list(window=window)

    # draws the SkeletonStim on the window
    def draw(self):
        for i in range(len(self._shape_list)):
            self._shape_list[i].draw()

    # builds up the shape list with circles and squares
    def _build_shape_list(self, window):
        self._build_shape_list_helper(window, self.root)

    # helps build up shape list with recursion
    def _build_shape_list_helper(self, window, current):
        circle = visual.Circle(win=window,
                               units="pix",
                               radius=(self.thickness / 2),
                               edges=32,
                               fillColor="white",
                               pos=current.position)
        self._shape_list.append(circle)

        for i in range(len(current.connections)):
            rectangle = self._Rectangle(window=window,
                                  p0=current.position,
                                  p1=current.connections[i].position,
                                  thickness=self.thickness)
            self._shape_list.append(rectangle)
            self._build_shape_list_helper(window, current.connections[i])
