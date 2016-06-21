# @author Drew McCoy <drewm@alleninstitute.org>
# setting up stimuli for experiment

# imports
from psychopy import visual, core, event, monitors
from shapes import SkeletonNode, SkeletonStim
from random import shuffle
import time
import datetime
import copy
from stimulus_base import StimBase


class Stim(StimBase):

    def __init__(self, window, params, thickness, duration_on, duration_off, random):
        super(Stim, self).__init__(window=window, params=params)

        self.params = copy.deepcopy(params)
        self.window = window
        self.thickness = thickness
        self.duration_on = duration_on
        self.duration_off = duration_off
        self.stimuli = self.get_shapes(window, thickness) + [self.get_dots(window, thickness)]
        if random:
            shuffle(self.stimuli)

        self.start_datetime = datetime.datetime.now()
        self.mouse_id = 'test_stimulus_code'
        self.show_clock = True

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

        frame = 0
        stim_index = 0

        while self.active:

            if frame % 60 is 0:
                stim_index += 1
            self.stimuli[stim_index % len(self.stimuli)].draw()
            self.window.update()

            # if a key is pressed, set play to False
            if len(event.getKeys()) > 0:
                self.active = False
            event.clearEvents()

            # increment frame
            frame += 1


            if self.timer is not None and self.timer.getTime() - self.starttime >= duration:
                self.active = False

            #If it's time to toggle the stimulus, convert True to False and vice-versa
            if self.timer.getTime() >= self.next_stim_toggle:

                self.show_stim ^= True
                # reference into our durations tuple with the boolean
                self.next_stim_toggle += self.durations[int(self.show_stim)]

            #Log some stuff to stimuluslog to reconstruct later
            self.stimuluslog.append({'time':self.timer.getTime(),'frame':self.vsynccount,'state':self.show_stim})


            # Show clock for debugging purposes
            if self.show_clock == True:
                self.display_clock(self.window)
        # -------------------------------END MAIN LOOP-----------------------------------

        # cleanup
        win.close()
        core.quit()

    def get_shapes(self, window, thickness):
        # order 1
        # shape_0
        node_0b = SkeletonNode(position=(0, 100))
        node_0a = SkeletonNode(position=(0, -100), connections=[node_0b])
        shape_0 = SkeletonStim(window=window, root=node_0a, shape_id=0, thickness=thickness)

        # shape_1
        node_1b = SkeletonNode(position=(-100, 0))
        node_1a = SkeletonNode(position=(100, 0), connections=[node_1b])
        shape_1 = SkeletonStim(window=window, root=node_1a, shape_id=1, thickness=thickness)

        # shape_2
        node_2b = SkeletonNode(position=(-100, -100))
        node_2a = SkeletonNode(position=(100, 100), connections=[node_2b])
        shape_2 = SkeletonStim(window=window, root=node_2a, shape_id=2, thickness=thickness)


        # order 2
        # shape_3
        node_3c = SkeletonNode(position=(100, 50))
        node_3b = SkeletonNode(position=(100, -50))
        node_3a = SkeletonNode(position=(-100, 0), connections=[node_3b, node_3c])
        shape_3 = SkeletonStim(window=window, root=node_3a, shape_id=3, thickness=thickness)

        # shape_4
        node_4c = SkeletonNode(position=(-50, 100))
        node_4b = SkeletonNode(position=(-50, -100))
        node_4a = SkeletonNode(position=(50, 0), connections=[node_4b, node_4c])
        shape_4 = SkeletonStim(window=window, root=node_4a, shape_id=4, thickness=thickness)

        # order 3
        # shape_5
        node_5d = SkeletonNode(position=(-50, 100))
        node_5c = SkeletonNode(position=(-50, 0), connections=[node_5d])
        node_5b = SkeletonNode(position=(50, 0), connections=[node_5c])
        node_5a = SkeletonNode(position=(50, -100), connections=[node_5b])
        shape_5 = SkeletonStim(window=window, root=node_5a, shape_id=5, thickness=thickness)

        # shape_6
        node_6d = SkeletonNode(position=(-100, 50))
        node_6c = SkeletonNode(position=(100, 50))
        node_6b = SkeletonNode(position=(0, -100))
        node_6a = SkeletonNode(position=(0, 0), connections=[node_6b, node_6c, node_6d])
        shape_6 = SkeletonStim(window=window, root=node_6a, shape_id=6, thickness=thickness)

        # shape_7
        node_7d = SkeletonNode(position=(-100, 100))
        node_7c = SkeletonNode(position=(100, 100), connections=[node_7d])
        node_7b = SkeletonNode(position=(100, -100), connections=[node_7c])
        node_7a = SkeletonNode(position=(-100, -100), connections=[node_7b])
        shape_7 = SkeletonStim(window=window, root=node_7a, shape_id=7, thickness=thickness)

        # shape_8
        node_8d = SkeletonNode(position=(0, 100))
        node_8c = SkeletonNode(position=(-50, -100))
        node_8b = SkeletonNode(position=(50, -100))
        node_8a = SkeletonNode(position=(0, 0), connections=[node_8b, node_8c, node_8d])
        shape_8 = SkeletonStim(window=window, root=node_8a, shape_id=8, thickness=thickness)

        # shape_9
        node_9d = SkeletonNode(position=(100, 0))
        node_9c = SkeletonNode(position=(75, -50))
        node_9b = SkeletonNode(position=(75, 50))
        node_9a = SkeletonNode(position=(0, 0), connections=[node_9b, node_9c, node_9d])
        shape_9 = SkeletonStim(window=window, root=node_9a, shape_id=9, thickness=thickness)

        return [shape_0, shape_1, shape_2, shape_3, shape_4, shape_5, shape_6, shape_7, shape_8, shape_9]

    def get_dots(self, window, thickness):
        return visual.DotStim(win=window,
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

    stim.run(duration= 10*60)

    print ""
    print "min frame interval:",np.min(stim.vsyncintervals)
    print "max run clock interval:",np.max(stim.vsyncintervals)
    print "mean frame intervals:",np.mean(stim.vsyncintervals)
