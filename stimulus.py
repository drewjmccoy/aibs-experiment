"""@author Drew McCoy <drewm@alleninstitute.org>
Setting up stimuli for experiment
"""
# TODO mess with contrast

from psychopy import visual, core, event, monitors
from shapes import SkeletonNode, SkeletonStim, MotionStim
from random import shuffle
import time
import datetime
import copy
from stimulus_base import StimBase
from math import floor, ceil


class Stim(StimBase):

    def __init__(self, window, params, dot_size, shape_thickness,
                 shape_size, duration_on, duration_off, random):
        super(Stim, self).__init__(window=window, params=params)

        self.params = copy.deepcopy(params)
        self.window = window
        self.dot_size = dot_size
        self.shape_thickness = shape_thickness
        self.shape_size = shape_size
        self.duration_on = duration_on
        self.duration_off = duration_off
        self.random = random
        self.shapes = self.get_shapes(window, shape_thickness, shape_size)
        self.dots = self.get_dots(window, dot_size)
        self.stimuli =  self.shapes + self.dots
        self.num_stimuli = len(self.stimuli)
        if self.random:
            shuffle(self.stimuli)

        self.start_datetime = datetime.datetime.now()
        self.mouseid = 'test_stimulus_code'
        self.show_clock = True

        self.syncpulse = True
        self.syncsqr = True

        self._IO_signal_setup()

    def run(self, duration=5):
        self.timer = core.Clock()
        self.timer.reset()

        self.starttime = self.timer.getTime()
        self.stoptime = None

        if self.eyetracker:
            self.eyetracker.recordStart()

        #Let's start with the stimulus off
        self.show_stim = False
        self.next_stim_toggle = self.duration_off

        # ---------------------------------MAIN LOOP-------------------------------------

        # session setup
        frame = 0
        stim_index = 0
        interval_length = self.duration_on + self.duration_off
        last_interval_time = 0

        while self.active:

            # end session if time has expired
            if self.timer is not None and self.timer.getTime() - self.starttime >= duration:
                self.active = False

            # end session if any key is pressed
            if len(event.getKeys()) > 0:
                self.active = False
            event.clearEvents()

            # show clock for debugging purposes
            if self.show_clock == True:
                self.display_clock(self.window)

            # get and modularize the time for simplicity
            time = self.timer.getTime()
            interval_time = time % interval_length

            # change stimuli at the top of the interval, reset opacity
            if ceil(last_interval_time) == interval_length and floor(interval_time) == 0:
                stim_index += 1
                stim_index %= self.num_stimuli
                # self.stimuli[stim_index].setOpacity(0)

            stim_id = self.stimuli[stim_index].stimulus_id
            stim_type = self.stimuli[stim_index].stimulus_type
            # self.stimuli[stim_index].changeOpacity(.005)

            # show stimuli dependent on duration_on
            if interval_time < self.duration_on:
                self.show_stim = True
                self.stimuli[stim_index].draw()
            else:
                self.show_stim = False

            # self.window.update()

            # If it's time to toggle the stimulus, convert True to False and vice-versa
            # if self.timer.getTime() >= self.next_stim_toggle:
            #
            #     # ?
            #     # self.show_stim ^= True
            #     self.show_stim = not self.show_stim
                # reference into our durations tuple with the boolean
                # self.next_stim_toggle += self.durations[int(self.show_stim)]

            # log variables
            # TODO opasity/contrast
            self.stimuluslog.append({'time':time,
                                    'frame':frame,
                                    'stimuli shown':self.show_stim,
                                    'stimuli_id':stim_id,
                                    'stimuli_type':stim_type})

            # update variables
            frame += 1
            # ?
            # self.vsynccount += 1
            last_interval_time = interval_time

            self._checkLickSensor()
            self._checkEncoder()
            self._check_keys()
            self._check_response()
            self._flip()
            self._checkUDP()

        # -------------------------------END MAIN LOOP-----------------------------------

        # cleanup
        print "SHUTTING DOWN"
        self._finalize()
        # print self.stimuluslog
        # self.window.close()
        core.quit()

    def get_shapes(self, window, shape_thickness, shape_size):
        result = []

        # order 1
        # shape_0
        node_b = SkeletonNode(position=(0, 200))
        node_a = SkeletonNode(position=(0, -200), connections=[node_b])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=0, thickness=shape_thickness)
        result.append(shape)

        # shape_1
        node_b = SkeletonNode(position=(-200, 0))
        node_a = SkeletonNode(position=(200, 0), connections=[node_b])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=1, thickness=shape_thickness)
        result.append(shape)

        # shape_2
        node_b = SkeletonNode(position=(-200, -200))
        node_a = SkeletonNode(position=(200, 200), connections=[node_b])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=2, thickness=shape_thickness)
        result.append(shape)


        # order 2
        # shape_3
        node_c = SkeletonNode(position=(200, 100))
        node_b = SkeletonNode(position=(200, -100))
        node_a = SkeletonNode(position=(-200, 0), connections=[node_b, node_c])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=3, thickness=shape_thickness)
        result.append(shape)

        # shape_4
        node_c = SkeletonNode(position=(-100, 200))
        node_b = SkeletonNode(position=(-100, -200))
        node_a = SkeletonNode(position=(100, 0), connections=[node_b, node_c])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=4, thickness=shape_thickness)
        result.append(shape)

        # order 3
        # shape_5
        node_d = SkeletonNode(position=(-100, 200))
        node_c = SkeletonNode(position=(-100, 0), connections=[node_d])
        node_b = SkeletonNode(position=(100, 0), connections=[node_c])
        node_a = SkeletonNode(position=(100, -200), connections=[node_b])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=5, thickness=shape_thickness)
        result.append(shape)

        # shape_6
        node_d = SkeletonNode(position=(-200, 100))
        node_c = SkeletonNode(position=(200, 100))
        node_b = SkeletonNode(position=(0, -200))
        node_a = SkeletonNode(position=(0, 0), connections=[node_b, node_c, node_d])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=6, thickness=shape_thickness)
        result.append(shape)

        # shape_7
        node_d = SkeletonNode(position=(-200, 200))
        node_c = SkeletonNode(position=(200, 200), connections=[node_d])
        node_b = SkeletonNode(position=(200, -200), connections=[node_c])
        node_a = SkeletonNode(position=(-200, -200), connections=[node_b])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=7, thickness=shape_thickness)
        result.append(shape)

        # shape_8
        node_d = SkeletonNode(position=(0, 200))
        node_c = SkeletonNode(position=(-100, -200))
        node_b = SkeletonNode(position=(100, -200))
        node_a = SkeletonNode(position=(0, 0), connections=[node_b, node_c, node_d])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=8, thickness=shape_thickness)
        result.append(shape)

        # shape_9
        node_d = SkeletonNode(position=(200, 0))
        node_c = SkeletonNode(position=(150, -200))
        node_b = SkeletonNode(position=(150, 200))
        node_a = SkeletonNode(position=(-200, 0), connections=[node_b, node_c, node_d])
        shape = SkeletonStim(window=window, root=node_a, stimulus_id=9, thickness=shape_thickness)
        result.append(shape)

        return result

    def get_dots(self, window, dot_size):
        result =[]

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=0,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=10)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=0,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=11)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=.5,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=12)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=.5,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=13)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=.9,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=14)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=0,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=15)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=0,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=16)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=.5,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=17)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=.5,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=18)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=50,
                            coherence=.9,
                            field_size=(500, 400),
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=19)
        result.append(dots)

        return result

if __name__ == "__main__":
    import dorsal_ventral_experiment
