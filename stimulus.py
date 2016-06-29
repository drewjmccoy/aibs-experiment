# @author Drew McCoy <drewm@alleninstitute.org>
# setting up stimuli for experiment
# TODO mess with contrast

# imports
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
        self.stimuli =  self.dots
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
        # order 1
        # shape_0
        node_0b = SkeletonNode(position=(0, 200))
        node_0a = SkeletonNode(position=(0, -200), connections=[node_0b])
        shape_0 = SkeletonStim(window=window, root=node_0a, stimulus_id=0, thickness=shape_thickness)

        # shape_1
        node_1b = SkeletonNode(position=(-200, 0))
        node_1a = SkeletonNode(position=(200, 0), connections=[node_1b])
        shape_1 = SkeletonStim(window=window, root=node_1a, stimulus_id=1, thickness=shape_thickness)

        # shape_2
        node_2b = SkeletonNode(position=(-200, -200))
        node_2a = SkeletonNode(position=(200, 200), connections=[node_2b])
        shape_2 = SkeletonStim(window=window, root=node_2a, stimulus_id=2, thickness=shape_thickness)


        # order 2
        # shape_3
        node_3c = SkeletonNode(position=(200, 100))
        node_3b = SkeletonNode(position=(200, -100))
        node_3a = SkeletonNode(position=(-200, 0), connections=[node_3b, node_3c])
        shape_3 = SkeletonStim(window=window, root=node_3a, stimulus_id=3, thickness=shape_thickness)

        # shape_4
        node_4c = SkeletonNode(position=(-100, 200))
        node_4b = SkeletonNode(position=(-100, -200))
        node_4a = SkeletonNode(position=(100, 0), connections=[node_4b, node_4c])
        shape_4 = SkeletonStim(window=window, root=node_4a, stimulus_id=4, thickness=shape_thickness)

        # order 3
        # shape_5
        node_5d = SkeletonNode(position=(-100, 200))
        node_5c = SkeletonNode(position=(-100, 0), connections=[node_5d])
        node_5b = SkeletonNode(position=(100, 0), connections=[node_5c])
        node_5a = SkeletonNode(position=(100, -200), connections=[node_5b])
        shape_5 = SkeletonStim(window=window, root=node_5a, stimulus_id=5, thickness=shape_thickness)

        # shape_6
        node_6d = SkeletonNode(position=(-200, 100))
        node_6c = SkeletonNode(position=(200, 100))
        node_6b = SkeletonNode(position=(0, -200))
        node_6a = SkeletonNode(position=(0, 0), connections=[node_6b, node_6c, node_6d])
        shape_6 = SkeletonStim(window=window, root=node_6a, stimulus_id=6, thickness=shape_thickness)

        # shape_7
        node_7d = SkeletonNode(position=(-200, 200))
        node_7c = SkeletonNode(position=(200, 200), connections=[node_7d])
        node_7b = SkeletonNode(position=(200, -200), connections=[node_7c])
        node_7a = SkeletonNode(position=(-200, -200), connections=[node_7b])
        shape_7 = SkeletonStim(window=window, root=node_7a, stimulus_id=7, thickness=shape_thickness)

        # shape_8
        node_8d = SkeletonNode(position=(0, 200))
        node_8c = SkeletonNode(position=(-100, -200))
        node_8b = SkeletonNode(position=(100, -200))
        node_8a = SkeletonNode(position=(0, 0), connections=[node_8b, node_8c, node_8d])
        shape_8 = SkeletonStim(window=window, root=node_8a, stimulus_id=8, thickness=shape_thickness)

        # shape_9
        node_9d = SkeletonNode(position=(200, 0))
        node_9c = SkeletonNode(position=(150, -100))
        node_9b = SkeletonNode(position=(150, 100))
        node_9a = SkeletonNode(position=(-200, 0), connections=[node_9b, node_9c, node_9d])
        shape_9 = SkeletonStim(window=window, root=node_9a, stimulus_id=9, thickness=shape_thickness)

        return [shape_0, shape_1, shape_2, shape_3, shape_4, shape_5, shape_6, shape_7, shape_8, shape_9]

    def get_dots(self, window, dot_size):
        dots_0 = MotionStim(window=window,
                          units='deg',
                          coherence=.1,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.01,
                          nDots=200,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=10)

        dots_1 = MotionStim(window=window,
                          units='deg',
                          coherence=.1,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.008,
                          nDots=200,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=11)

        dots_2 = MotionStim(window=window,
                          units='deg',
                          coherence=.1,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.005,
                          nDots=200,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=12)

        dots_3 = MotionStim(window=window,
                          units='deg',
                          coherence=.1,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.01,
                          nDots=400,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=13)

        dots_4 = MotionStim(window=window,
                          units='deg',
                          coherence=.1,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.005,
                          nDots=400,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=14)

        dots_5 = MotionStim(window=window,
                          units='deg',
                          coherence=.9,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.01,
                          nDots=200,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=15)

        dots_6 = MotionStim(window=window,
                          units='deg',
                          coherence=.9,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.008,
                          nDots=200,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=16)

        dots_7 = MotionStim(window=window,
                          units='deg',
                          coherence=.9,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.005,
                          nDots=200,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=17)

        dots_8 = MotionStim(window=window,
                          units='deg',
                          coherence=.9,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.01,
                          nDots=400,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=18)

        dots_9 = MotionStim(window=window,
                          units='deg',
                          coherence=.9,
                          fieldSize=(100,100),
                          color=[-1],
                          dotSize=dot_size,
                          dotLife=-1,
                          noiseDots='direction',
                          signalDots='same',
                          speed=0.005,
                          nDots=400,
                          fieldShape='sqr',
                          dir=90,
                          stimulus_id=19)

        return [dots_0, dots_1, dots_2, dots_3, dots_4, dots_5, dots_6, dots_7, dots_8, dots_9]

if __name__ == "__main__":
    # PARAMETERS GO HERE
    thickness = 10
    duration_on = 1
    duration_off = 1
    random = True

    mon = monitors.Monitor('testMonitor')#fetch the most recent calib for this monitor
    mon.setDistance(15)
    window = visual.Window(monitor=mon, units="deg",fullscr = True,screen =0,allowGUI=False)
    window.setMouseVisible(False)

    params = {'domain':'time'}
    stim = Stim(window=window,
                params=params,
                thickness=thickness,
                duration_on=duration_on,
                duration_off=duration_off,
                random=random)

    stim.run(duration=5*60)

    print ""
    print "min frame interval:",np.min(stim.vsyncintervals)
    print "max run clock interval:",np.max(stim.vsyncintervals)
    print "mean frame intervals:",np.mean(stim.vsyncintervals)
