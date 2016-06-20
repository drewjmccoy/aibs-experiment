# -*- coding: utf-8 -*-
"""

@author: dougo
"""


from psychopy import visual,logging,monitors,core,event,sound
from pyglet.window import key
import socket
import numpy as np
import time
import datetime
import copy
import itertools
from random import shuffle
import os
from warnings import warn
import sys
import pandas as pd

if sys.platform == 'win32':
    import win32api

from aibs.logger import logger
from aibs.datastream import DataStream
from aibs.Core import wecanpicklethat,SyncSquare,getPlatformInfo,getMonitorInfo,getdirectories,checkDirs,getConfig,ImageStimNumpyuByte
try:
    from aibs.iodaq import DigitalOutput, DigitalInput,AnalogInput, AnalogOutput
except Exception, e:
    print "No NI boards found.", e

from StimulusBase import StimBase

AGENT_IP = "127.0.0.1"
AGENT_PORT = 1111

class Stim(StimBase):
    """docstring for Stim
        Inputs:
        1) a psychopy window, "window"
        2) a dictionary of parameters, "params", each element is set as an
            attribute of the class.
    """

    def __init__(self, window, params={}):

        super(Stim, self).__init__(window=window, params=params)  # Sets basic attributes, sets up window.

        self.params = copy.deepcopy(params)

        print "PARAMS:",self.params

        self.startdatetime = datetime.datetime.now()

        self.mouseid = 'test_stimulus_code'

        self.show_clock = True
        self.play_sounds = False

        self.on_duration = 2 #seconds
        self.off_duration = 4 #seconds

        self.durations = (self.off_duration,self.on_duration) #put these in a tuple to use later

        #take in passed parameters from a script, overwrite defaults
        self._apply_passed_params()

        self._IO_signal_setup()

        self.grating = []
        self.grating.append(visual.GratingStim(window, pos=(-25,0),tex = 'sin',color=1, phase=0.25,mask='raisedCos',maskParams={'fringeWidth':0.7}, ori=0,contrast=1,size=[75,75],sf=0.08, units="deg",texRes=2**8))

        self.bgstim = visual.GratingStim(window, tex = None,color=-0.8,mask=None, size=[1920,1200], pos=[0,0],units="pix")
        self.blank = visual.GratingStim(window, tex = None,color=0,mask=None, size=[1,1], pos=[0,0],units="deg")



    def run(self,duration=5):
        """Main execution loop"""

        self.timer = core.Clock()
        self.timer.reset()

        print "in run"
        print "PARAMS:",self.params

        self.starttime = self.timer.getTime()
        self.stoptime = None

        if self.eyetracker:
            self.eyetracker.recordStart()

        #Let's start with the stimulus off
        self.show_stim = False
        self.next_stim_toggle = self.off_duration


        #START OF MAIN EXECUTION LOOP: COMPARES TIME TO EXPECTED DURATION
        #========================================================================================================================================
        while self.active == True:

            if self.timer is not None and self.timer.getTime() - self.starttime >= duration:
                self.active = False

            #If it's time to toggle the stimulus, convert True to False and vice-versa
            if self.timer.getTime() >= self.next_stim_toggle:

                self.show_stim^=True
                self.next_stim_toggle += self.durations[int(self.show_stim)] #reference into our durations tuple with the boolean

            # A print statement for troubleshooting
            print self.vsynccount,"stim state = ",self.show_stim,"  next stim state change at: ",self.next_stim_toggle

            #Show the grating stimulus, pass the boolean "show_stim" to determine whether or not it's actually rendered
            self.grating_stim(self.window,draw_central=self.show_stim)

            #Log some stuff to stimuluslog to reconstruct later
            self.stimuluslog.append({'time':self.timer.getTime(),'frame':self.vsynccount,'state':self.show_stim})


            # Show clock for debugging purposes
            if self.show_clock == True:
                self.display_clock(self.window)


            #Run methods for hardware checking, flip monitor
            self._checkLickSensor()
            self._checkEncoder()
            self._check_keys()
            self._check_response()
            self._flip()
            self._checkUDP()

        #END OF MAIN EXECUTION LOOP:
        #========================================================================================================================================

        print "SHUTTING DOWN"
        self._finalize()




if __name__ == '__main__':
    mon = monitors.Monitor('testMonitor')#fetch the most recent calib for this monitor
    mon.setDistance(15)
    window = visual.Window(monitor=mon, units="deg",fullscr = True,screen =0,allowGUI=False)
    window.setMouseVisible(False)
    params = {'domain':'time'}
    stim = Stim(window=window,params=params)
    stim.run(duration= 10*60)
    print ""
    print "min frame interval:",np.min(stim.vsyncintervals)
    print "max run clock interval:",np.max(stim.vsyncintervals)
    print "mean frame intervals:",np.mean(stim.vsyncintervals)
