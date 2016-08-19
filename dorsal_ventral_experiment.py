"""@author Drew McCoy <drewm@alleninstitute.org>
Main script for the experiment
"""

import sys
# sys.path.append(r'\\AIBSDATA2\nc-ophys\Doug\Drew_Summer_Project\Experiment5Code')
print sys.path
from stimulus import Stim
from psychopy import visual,logging,monitors,core,event
import numpy as np

# RENAME SOME KEYS IN THE KWARGS_DICT TO MATCH YOUR FUNCTION'S KEYS
def reformat_mouse_user(kwargs_dict):
    # pop removes a key from a dictionary and returns the value that was associated with that key
    kwargs_dict["mouseid"] = kwargs_dict.pop("mouse_id")
    kwargs_dict["userid"] = kwargs_dict.pop("user_id")

def run_script(**kwargs):

        Duration = 60 # minutes
        monitor_name = 'testMonitor'
        # monitor_name = 'GammaCorrect30'

        mouseid = 'testmouse' # TODO CHANGE BEFORE EXPERIMENT

        show_clock = False # memory leaks when True

        # TODO change file directory for pkl

        dot_size = 46
        num_dots = 17
        shape_thickness = 90
        field_size = (250, 250)

        gray_periods = 1 # * (duration_on + duration_off) seconds
        repetitions = 8

        duration_on = 3
        duration_off = 3

        random = True

        viewing_distance = 15 # cms from screen

        performanceip = "w7dtmj37pct"
        performanceport = 9998

        params = {'mouseid':mouseid,
                'show_clock':show_clock,
                'performanceip':performanceip,
                'performanceport':performanceport,
                'viewing_distance':viewing_distance,
                'eyetracker':True,
                'eyetrackerIP':'W7DT710861',
                'dot_size': dot_size,
                'num_dots': num_dots,
                'shape_thickness': shape_thickness,
                'duration_on': duration_on,
                'duration_off': duration_off,
                'random':random,
                'field_size':field_size,
                'repetitions':repetitions,
                'gray_periods': gray_periods}

        try:
            reformat_mouse_user(kwargs)
        except:
            pass
        params.update(kwargs) # UPDATE THE PARAMS DICTIONARY WITH THE VALUES PASSED TO THE FUNCTION VIA KWARGS

        mon = monitors.Monitor(monitor_name) # fetch the most recent calib for this monitor
        mon.setDistance(viewing_distance)
        window = visual.Window(monitor=mon, units="deg",fullscr = True,size=(500, 500),screen =0,allowGUI=False,winType='pyglet')

        window.setMouseVisible(False)

        stim = Stim(window=window,
                    params=params,
                    dot_size=dot_size,
                    num_dots=num_dots,
                    shape_thickness=shape_thickness,
                    duration_on=duration_on,
                    duration_off=duration_off,
                    random=random,
                    field_size=field_size,
                    repetitions=repetitions,
                    gray_periods=gray_periods,
                    show_clock=show_clock,
                    mouseid=mouseid)

        stim.run(duration=Duration*60)
        # stim.run(duration=30)

        print ""
        print "===============Done==============="
        print "min frame interval (ms):",np.min(stim.vsyncintervals)
        print "max frame interval (ms):",np.max(stim.vsyncintervals)
        print "mean frame intervals (ms):",np.mean(stim.vsyncintervals)
        print "total dropped frames: ",np.sum(stim.vsyncintervals>20)
        print ""
        print "number of rewards:",len(stim.rewards)
        print "volume per reward:",stim.rewardvol
        print "volume:",len(stim.rewards)*stim.rewardvol

def parse_serial_json(serial_json):
    import json
    return json.loads(serial_json)

import sys

if len(sys.argv) > 1:
    json_kwargs = parse_serial_json(sys.argv[1])
    run_script(**json_kwargs)
else:
    run_script()
