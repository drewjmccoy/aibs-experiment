"""@author Drew McCoy <drewm@alleninstitute.org>
Setting up stimuli for experiment
"""
# TODO mess with contrast
# TODO implement Shawn's interval changes

from psychopy import visual, core, event, monitors
from shapes import SkeletonNode, SkeletonStim, MotionStim
from random import shuffle
import time
import datetime
import copy
from stimulus_base import StimBase
from math import floor, ceil

import pylab
from memory_util import total_size


class Stim(StimBase):

    def __init__(self, window, params, dot_size, num_dots, shape_thickness,
                 duration_on, duration_off, random, field_size, repetitions,
                 gray_periods, show_clock):
        super(Stim, self).__init__(window=window, params=params)

        self.params = copy.deepcopy(params)
        self.window = window
        self.dot_size = dot_size
        self.num_dots = num_dots
        self.shape_thickness = shape_thickness
        self.duration_on = duration_on
        self.duration_off = duration_off
        self.random = random
        self.field_size = field_size
        self.show_clock = show_clock
        self.repetitions = repetitions
        self.shapes = self.get_shapes(window, shape_thickness)
        self.dots = self.get_dots(window, dot_size, field_size, num_dots)
        self.gray_periods = gray_periods
        self.stimuli =  self.dots + self.shapes
        if self.random:
            shuffle(self.shapes)
            shuffle(self.dots)
            shuffle(self.stimuli)

        self.start_datetime = datetime.datetime.now()
        self.mouseid = 'test_stimulus_code'

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

        # ---------------------------------MAIN LOOP-------------------------------------

        # session setup
        frame = 0
        stim_index = 0
        interval_length = self.duration_on + self.duration_off
        last_interval_time = 0
        stim_set = self.shapes
        repetition = 0
        gray_index = 0
        show_stim = False
        gray_period = False

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
                if gray_period:
                    gray_index += 1
                else:
                    stim_index += 1
                    stim_index %= len(stim_set)
                    if stim_index == 0:
                        repetition += 1
                        if self.random:
                            shuffle(stim_set)

            # stimulus = stim_set[stim_index]
            # stim_id = stimulus.stimulus_id
            # stim_type = stimulus.stimulus_type

            # show stimuli dependent on duration_on
            if repetition < self.repetitions:
                gray_period = False
                if interval_time < self.duration_on:
                    show_stim = True
                    stim_set[stim_index].draw()
                else:
                    show_stim = False
            else:
                gray_period = True
                show_stim = False
                if gray_index >= self.gray_periods:
                    repetition = 0
                    gray_index = 0
                    if stim_set is self.shapes:
                        stim_set = self.dots
                    else:
                        stim_set = self.shapes

            try:
                last_frame_interval = self.window.frameIntervals[-1]
            except:
                last_frame_interval = 0.0

            # log variables
            self.stimuluslog.append({'time':time,
                                    'frame':frame,
                                    'repetition': repetition,
                                    'stimuli shown':show_stim,
                                    'stimuli_id':stim_set[stim_index].stimulus_id,
                                    'stimuli_type':stim_set[stim_index].stimulus_type,
                                    'gray_period': gray_period,
                                    'last_frame_interval': last_frame_interval})

            # update variables
            frame += 1
            last_interval_time = interval_time

            self.window.update()
            # self._checkLickSensor()
            # self._checkEncoder()
            # self._check_keys()
            # self._check_response()
            # self._flip()
            # self._checkUDP()

            if len(self.window.frameIntervals) != 0:
                if self.window.frameIntervals[-1] > .020:
                    print "DROPPED FRAME"
                    print str(self.window.frameIntervals[-1])

        # -------------------------------END MAIN LOOP-----------------------------------

        # cleanup
        print "SHUTTING DOWN"
        print total_size(self.stimuluslog)
        self._finalize()
        core.quit()

    def get_shapes(self, window, shape_thickness):
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

    def get_dots(self, window, dot_size, field_size, num_dots):
        result =[]

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=0,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=10)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=0,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=11)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=.5,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=12)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=.5,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=13)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=.9,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=5,
                            stimulus_id=14)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=0,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=15)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=0,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=16)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=.5,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=17)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=.5,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=18)
        result.append(dots)

        dots = MotionStim(window=window,
                            n_dots=num_dots,
                            coherence=.9,
                            field_size=field_size,
                            dot_size=dot_size,
                            speed=10,
                            stimulus_id=19)
        result.append(dots)

        return result

    def get_gray_periods(self, n):
        result = []
        for i in range(n):
            result.append(0)
        return result

if __name__ == "__main__":
    import dorsal_ventral_experiment
