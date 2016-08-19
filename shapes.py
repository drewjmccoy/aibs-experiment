"""@author Drew McCoy <drewm@alleninstitute.org>
Defines Rectangle, SkeletonNode, SkeletonStim
"""

from psychopy import visual
import math, random

class SkeletonNode(object):
    """A node of a skeleton data structure
    SkeletonNode(position, connections)
    """

    def __init__(self, position=(0, 0), connections=[]):
        """Initializes node"""

        self.position = position
        self.connections = connections

class SkeletonStim(object):
    """A shape stimulus."""

    class _Rectangle(object):
        """Defines a Rectangle ShapeStim, given two end points."""

        def __init__(self, window, p0=(-100, 0), p1=(100, 0), thickness=20):
            """Initializes the Rectangle."""

            self._rectangle = visual.Rect(win=window,
                                          units="pix",
                                          fillColor="black",
                                          lineColor="black",
                                          width=self._getWidth(p0, p1),
                                          height=thickness,
                                          pos=self._getPosition(p0, p1),
                                          ori=self._getOrientation(p0, p1))
            self.opacity = 1.0

        def draw(self):
            """Draws the stimulus on the window."""
            self._rectangle.draw()

        def _getWidth(self, p0, p1):
            """Returns the width of the Rectangle."""
            result = math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
            return result

        def _getPosition(self, p0, p1):
            """Returns the position (midpoint) of the Rectangle."""

            x = (p1[0] + p0[0]) / 2 # Midpoint formula
            y = (p1[1] + p0[1]) / 2

            return (x, y)

        def _getOrientation(self, p0, p1):
            """Returns the orientation of the Rectangle in degrees - 0 is up, increasing
            clockwise.
            """
            # Get change y and x
            dy = p1[1] - p0[1]
            dx = p1[0] - p0[0]

            # If slope is undefined
            if dx is 0:
                if dy < 0:
                    return 90
                else:
                    return 270

            # Get temp radians of orientation (neg b/c psychopy is weird)
            rad = -math.atan2(dy, dx)

            # To degrees
            deg = math.degrees(rad)

            return deg

    def __init__(self, window, root, stimulus_id=0, thickness=20):
        """Initializes stimulus."""
        self.window = window
        self.root = root
        self.stimulus_id = stimulus_id
        self.thickness = thickness
        self.stimulus_type = "shape"

        # List of circles and rectangles that make up the shape
        self._shape_list = []

        # Build up shape list
        self._build_shape_list(window=window)

    def draw(self):
        """Draws the SkeletonStim on the window."""
        for i in range(len(self._shape_list)):
            self._shape_list[i].draw()

    def _build_shape_list(self, window):
        """Builds up the shape list with circles and squares."""
        self._build_shape_list_helper(window, self.root)

    def _build_shape_list_helper(self, window, current):
        """Helps build up shape list with recursion."""
        circle = visual.Circle(win=window,
                               units="pix",
                               radius=(self.thickness / 2),
                               edges=32,
                               fillColor="black",
                               lineColor="black",
                               pos=current.position)
        self._shape_list.append(circle)

        for i in range(len(current.connections)):
            rectangle = self._Rectangle(window=window,
                                  p0=current.position,
                                  p1=current.connections[i].position,
                                  thickness=self.thickness)
            self._shape_list.append(rectangle)
            self._build_shape_list_helper(window, current.connections[i])

class MotionStim(object):
    """A motion stimulus."""

    class _Dot:
        """A dot in the motion stimulus."""

        def __init__(self, window, radius=5, position=(0, 0), direction=0, speed=1,
                     field_size=(100, 100), controlled=False):
            """Initializes the dot."""
            self.position = position
            self.direction = direction
            self.speed = speed
            self.field_size = field_size
            self.controlled = controlled
            self.dot = visual.Circle(win=window,
                                     units="pix",
                                     radius=radius,
                                     edges=32,
                                     fillColor="black",
                                     lineColor="black",
                                     pos=position)

        def draw(self):
            """Draws the dot on the window."""
            self.dot.draw()
            self._update_position()

        def _update_position(self):
            """Updates the position of the dot on the window."""
            x = self.position[0]
            y = self.position[1]

            if math.fabs(int(x)) >= self.field_size[0] or math.fabs(int(y)) >= self.field_size[1]:
                # If dot is out of bounds, reset it
                x = random.randint(-self.field_size[0] + 1, self.field_size[0] - 1)
                if self.controlled:
                    y = -self.field_size[1] + 1
                else:
                    self.direction = random.randint(0, 359)
                    y = random.randint(-self.field_size[1] + 1, self.field_size[1] - 1)
                self.position = (x, y)
            else:
                # Normal movement
                dx = self.speed * math.cos(math.radians(self.direction))
                dy = self.speed * math.sin(math.radians(self.direction))
                self.position = (x + dx, y + dy)

            self.dot.pos = self.position

    def __init__(self, window, n_dots=100, coherence=.5, field_size=(100, 100),
                 dot_size=10, speed=1, stimulus_id=10):
        """Initializes the MotionStim."""
        self.window = window
        self.n_dots = n_dots
        self.coherence = coherence
        self.field_size = field_size
        self.dot_size = dot_size
        self.speed = speed
        self.stimulus_id = stimulus_id
        self.stimulus_type = "motion"
        self.dots = self._get_dots()

    def draw(self):
        """Draws the dot on the window."""
        for dot in self.dots:
            dot.draw()

    def _get_dots(self):
        """Returns a list of dots with random directions and positions."""
        result = []
        for i in range(self.n_dots):
            direction = random.randint(0, 359)
            x = random.randint(-self.field_size[0] + 1, self.field_size[0] - 1)
            y = random.randint(-self.field_size[1] + 1, self.field_size[1] - 1)
            controlled = False

            if i < self.coherence * self.n_dots:
                controlled = True
                direction = 90

            dot = self._Dot(window=self.window,
                      radius=self.dot_size / 2,
                      position=(x, y),
                      direction=direction,
                      speed=self.speed,
                      field_size=self.field_size,
                      controlled=controlled)
            result.append(dot)

        return result

if __name__ == "__main__":
    import dorsal_ventral_experiment
