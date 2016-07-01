# @author Drew McCoy <drewm@alleninstitute.org>
# setting up stimuli for experiment

# imports
from psychopy import visual, core, event
from shapes import SkeletonNode, SkeletonStim
from random import shuffle
import time
import datetime

class Stim(object):

    def __init__(self, window, thickness, duration_on, duration_off, random):
        self.window = window
        self.thickness = thickness
        self.duration_on = duration_on
        self.duration_off = duration_off
        self.stimuli = ''.join(self.get_shape(window, thickness),
                               self.get_dots(window, thickness))
        if random:
            shuffle(self.stimuli)

        self.start_datetime = datetime.datetime.now()
        self.mouse_id = 'test_stimulus_code'


    def run(self):

        # ---------------------------------MAIN LOOP-------------------------------------

        # loop setup
        play = True
        frame = 0

        while play:
            shapes[frame / 100 % 10].draw()
            dots.draw()
            win.update()

            # if a key is pressed, set play to False
            if len(event.getKeys()) > 0:
                play = False
            event.clearEvents()

            # increment frame
            frame += 1
        # -------------------------------END MAIN LOOP-----------------------------------

        # cleanup
        win.close()
        core.quit()

    def get_shapes(window, thickness):
        # order 1
        # shape_0
        node_0b = SkeletonNode(position=(0, 100))
        node_0a = SkeletonNode(position=(0, -100), connections=[node_0b])
        shape_0 = SkeletonStim(window=win, root=node_0a, stimulus_id=0, thickness=thickness)

        # shape_1
        node_1b = SkeletonNode(position=(-100, 0))
        node_1a = SkeletonNode(position=(100, 0), connections=[node_1b])
        shape_1 = SkeletonStim(window=win, root=node_1a, stimulus_id=1, thickness=thickness)

        # shape_2
        node_2b = SkeletonNode(position=(-100, -100))
        node_2a = SkeletonNode(position=(100, 100), connections=[node_2b])
        shape_2 = SkeletonStim(window=win, root=node_2a, stimulus_id=2, thickness=thickness)


        # order 2
        # shape_3
        node_3c = SkeletonNode(position=(100, 50))
        node_3b = SkeletonNode(position=(100, -50))
        node_3a = SkeletonNode(position=(-100, 0), connections=[node_3b, node_3c])
        shape_3 = SkeletonStim(window=win, root=node_3a, stimulus_id=3, thickness=thickness)

        # shape_4
        node_4c = SkeletonNode(position=(-50, 100))
        node_4b = SkeletonNode(position=(-50, -100))
        node_4a = SkeletonNode(position=(50, 0), connections=[node_4b, node_4c])
        shape_4 = SkeletonStim(window=win, root=node_4a, stimulus_id=4, thickness=thickness)

        # order 3
        # shape_5
        node_5d = SkeletonNode(position=(-50, 100))
        node_5c = SkeletonNode(position=(-50, 0), connections=[node_5d])
        node_5b = SkeletonNode(position=(50, 0), connections=[node_5c])
        node_5a = SkeletonNode(position=(50, -100), connections=[node_5b])
        shape_5 = SkeletonStim(window=win, root=node_5a, stimulus_id=5, thickness=thickness)

        # shape_6
        node_6d = SkeletonNode(position=(-100, 50))
        node_6c = SkeletonNode(position=(100, 50))
        node_6b = SkeletonNode(position=(0, -100))
        node_6a = SkeletonNode(position=(0, 0), connections=[node_6b, node_6c, node_6d])
        shape_6 = SkeletonStim(window=win, root=node_6a, stimulus_id=6, thickness=thickness)

        # shape_7
        node_7d = SkeletonNode(position=(-100, 100))
        node_7c = SkeletonNode(position=(100, 100), connections=[node_7d])
        node_7b = SkeletonNode(position=(100, -100), connections=[node_7c])
        node_7a = SkeletonNode(position=(-100, -100), connections=[node_7b])
        shape_7 = SkeletonStim(window=win, root=node_7a, stimulus_id=7, thickness=thickness)

        # shape_8
        node_8d = SkeletonNode(position=(0, 100))
        node_8c = SkeletonNode(position=(-50, -100))
        node_8b = SkeletonNode(position=(50, -100))
        node_8a = SkeletonNode(position=(0, 0), connections=[node_8b, node_8c, node_8d])
        shape_8 = SkeletonStim(window=win, root=node_8a, stimulus_id=8, thickness=thickness)

        # shape_9
        node_9d = SkeletonNode(position=(100, 0))
        node_9c = SkeletonNode(position=(75, -50))
        node_9b = SkeletonNode(position=(75, 50))
        node_9a = SkeletonNode(position=(0, 0), connections=[node_9b, node_9c, node_9d])
        shape_9 = SkeletonStim(window=win, root=node_9a, stimulus_id=9, thickness=thickness)

        return [shape_0, shape_1, shape_2, shape_3, shape_4, shape_5, shape_6, shape_7, shape_8, shape_9]

    def get_dots(self, window, thickness):
        return visual.DotStim(win=win,
                               units='deg',
                               coherence=0.5,
                               fieldSize=(50,50),
                               color=[-1],
                               dotSize=thickness,
                               dotLife=20,
                               noiseDots='direction',
                               signalDots='same',
                               speed=0.01,
                               nDots=500,
                               fieldShape='circle',
                               dir=90)

if __name__ == "__main__":
    # PARAMETERS GO HERE
    thickness = 20
    duration_on = 2
    duration_off = 4
    randow = True

    # create a window
    window = visual.Window(monitor="testMonitor",
                        fullscr=True,
                        units="deg")
    stim = Stim(window, thickness, duration_on, duration_off, random)
