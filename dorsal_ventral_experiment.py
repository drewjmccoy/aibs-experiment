import sys
sys.path.append(r'//aibsdata2/nc-ophys/Doug/Stimulus_Code')
print sys.path
from stimulus import Stim
from psychopy import visual,logging,monitors,core,event
import numpy as np

def reformat_mouse_user(kwargs_dict): # RENAME SOME KEYS IN THE KWARGS_DICT TO MATCH YOUR FUNCTION'S KEYS
    # pop removes a key from a dictionary and returns the value that was associated with that key
    kwargs_dict["mouseid"] = kwargs_dict.pop("mouse_id")
    kwargs_dict["userid"] = kwargs_dict.pop("user_id")

def run_script(**kwargs):

        Duration = 30 # minutes
        monitor_name = 'testMonitor'
        # monitor_name = 'GammaCorrect30'

        mouseid = 'testmouse'
        # mouseid = 'testmouse'

        show_clock = True

        ## Put all parameters you'll want control over here:
        dot_size = 46
        num_dots = 2
        shape_thickness = 90
        field_size = (600, 500)
        gray_periods = 1 # * (duration_on + duration_off) seconds
        repititions = 2

        duration_on = 1
        duration_off = 1

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
                'repititions':repititions,
                'gray_periods': gray_periods}

        try:
            reformat_mouse_user(kwargs)
        except:
            pass
        params.update(kwargs) # UPDATE THE PARAMS DICTIONARY WITH THE VALUES PASSED TO THE FUNCTION VIA KWARGS

        mon = monitors.Monitor(monitor_name)# fetch the most recent calib for this monitor
        mon.setDistance(viewing_distance)
        # window = visual.Window(monitor=mon, units="deg",fullscr = False,size=(100, 100),screen =0,allowGUI=False,winType='pyglet')
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
                    repititions=repititions,
                    gray_periods=gray_periods,
                    show_clock=show_clock)

        stim.run(duration=Duration*60)

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
