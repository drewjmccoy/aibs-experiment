# -*- coding: utf-8 -*-
"""

@author: dougo
"""


from psychopy import visual, logging, monitors, core, event
from pyglet.window import key
import socket
import numpy as np
import time
import datetime
import copy
import os
from warnings import warn
import sys

if sys.platform == 'win32':
    import win32api
from zro import Publisher
from aibs.logger import logger
from aibs.datastream import DataStream
from aibs.Core import wecanpicklethat,SyncSquare,getPlatformInfo,getMonitorInfo,getdirectories,checkDirs,getConfig
try:
    from aibs.iodaq import DigitalOutput, DigitalInput,AnalogInput, AnalogOutput
except Exception, e:
    print "No NI boards found.", e

AGENT_IP = "127.0.0.1"
AGENT_PORT = 1111

class StimBase(Publisher):
    """docstring for Stim
        Inputs:
        1) a psychopy window, "window"
        2) a dictionary of parameters, "params", each element is set as an
            attribute of the class.
    """

    def __init__(self, window, params={}, rep_port=12000, pub_port=12001):

        super(StimBase, self).__init__(rep_port=rep_port,
                                       pub_port=pub_port)

        self.params = copy.deepcopy(params)

        print "PARAMS:",self.params

        self.task = 'DetectionOfChange'
        self.stage = None

        self.startdatetime = datetime.datetime.now()

        self.logdir = r'\\aibsdata\neuralcoding\behavior\data'
        self.backupdir = None

        self.window = window

        self.wwidth = self.window.size[0]
        self.wheight = self.window.size[1]
        self.monitor = self.window.monitor


        self.window.setRecordFrameIntervals(True)
        self.window._refreshThreshold=1/60.0+0.004 #60Hz display with a 4ms tolerance

        self.hide_mouse = True


        #set the log module to report warnings to the std output window (default is errors only)
        logging.console.setLevel(logging.WARNING)

        self.bg_luminance = 0.0

        #Timing signals
        self.syncpulse = False
        self.syncpulseport = 1
        self.syncpulselines = [3, 4, 5]

        self.syncsqr = True
        self.syncsqrloc = (910, -450)
        self.syncsqrcolorsequence = [-1,1]
        self.syncsqrsize = (100,100)
        self.syncsqrfreq = 60

        self.eyetrackerip = 'W7DT710861'
        self.eyetracker = True
        self.eyetrackerport = 10000
        self.trackeyepos = False
        self.moviefilename = None

        self.performanceip = None
        self.performanceport = None

        self.nidevice = 'Dev1'
        self.encodervinchannel = 0
        self.encodervsigchannel = 1
        self.invertdo = False
        self.diport = 0
        self.doport = 1

        self.rewardline = 0
        self.rewardlines = [0]
        self.airpuffline = 1

        self.controlstream = True
        self.datastream = None
        self.lickSensor = None

        self.volumelimit = 2.5


        #Log Variables
        self.vsynctimes = []
        self.vsyncintervals = []
        self.stimuluslog = []
        self.responselog = []
        self.triallog = []
        self.trialvars = None
        self.auditory_stimulus_log = []
        self.keylog = []
        self.vsynccount = 0
        self.trialcount = 0
        self.score = [0]
        self.vin = []  # encoder input voltage
        self.vsig = []  # encoder signal voltage
        self.dx = []
        self.rewards = []
        self.airpuffs = []
        self.commandrecord = []
        self.laps = []
        self.terrainlog = []

        #Timers and Flags
        self.active = True
        self.next_trial_time = -np.inf
        self.stim_on_time = None
        self.stim_on_frame = None
        self.show_stim = False
        self.mask_logged = False
        self.trial_hold = False #prevent a new trial from starting if True
        self.show_text_time = -np.inf
        self.response_time = -np.inf
        self.left_response_time = -np.inf
        self.right_response_time = -np.inf
        self.process_response = False
        self.decision = False
        self.rewarded = False
        self.message_color = -1
        self.last_frame = None
        self.paused = False

        self.fps = 60.0

        self.pos = (-25,0)

        self._lastDx = 0 #initialize this to avoid problems on first frame

        self.dropped_frame_count = 0
        self.dropped_frame_threshold = 100 #max warnings to print to screen

        #the ZRO stuff is here
        #self.__initZRO() did nothing and needs to be called after init_IO

    # def _initZRO(self, ip_port_tuple=("127.0.0.1", 9440), *args, **kwargs):
    #     """
    #     Imports ScriptSubscriber and uses it's static method: init_std_foraging,
    #     to override the following methods to attempt to enable ZRO rewards:
    #     - _reward
    #     - _checkUDP
    #     It will also add some methods as well:
    #     - _rewardZRO
    #     It also requires the following methods even though doesn't override them:
    #     - _finalize
    #     """
    #     try:
    #         import site
    #         sys.path.append(site.getsitepackages()[0])
    #         from scriptagent.script_subscriber import ScriptSubscriber
    #         ScriptSubscriber.init_std_foraging(self, ip_port_tuple, *args,
    #                                            **kwargs)
    #         print "Successfully loaded ScriptSubscriber"
    #     except ImportError as e:
    #         print "Could not load ScriptSubscriber"
    #         print e
    #         print ""


    def _IO_signal_setup(self):
        #INITIALIZE NIDAQ
        self._setupDAQ()
        ##TODO: Create syncpulse class.
        if self.syncpulse:
            self._syncpulseSetup()
        else:
            self.syncpulse = False

        if self.hide_mouse == True:
            self.window.setMouseVisible(False)
            self.window.winHandle.set_exclusive_mouse()
            self.window.winHandle.set_exclusive_keyboard()
            self.window.winHandle.set_mouse_visible(False)
            if sys.platform == 'win32':
                win32api.SetCursorPos((self.wwidth, self.wheight))


        #INITALIZE EYETRACKER
        print "INITIALIZING EYE TRACKER"
        if self.eyetracker == True:
            self._eyetrackerSetup()
            print "DONE"
        else:
            self.eyetracker = None

        #CREATE SYNC SQUARE (used for frame time measurement via photodiode)
        self.syncsqrBit = False
        if self.syncsqr:
            self.sync = SyncSquare(window=self.window,
                                   pos=self.syncsqrloc,
                                   frequency=self.syncsqrfreq,
                                   size=self.syncsqrsize,
                                   colorSequence=self.syncsqrcolorsequence)

        #INITIALIZE ENCODER
        self._encoderSetup()

        #INITIALIZE REWARD
        self._rewardSetup()

        #INITIALIZE AIRPUFFS
        self._airpuffSetup()

        #INITIALIZE LICK SENSOR
        print "about to set up lick sensor"
        print "++++++++++++++++++++++++++++++++++++++++"
        self._lickSensorSetup()
        self.lickData = []


        #INIT PERFORMANCE TRACKER IF POSSIBLE
        self._dataStreamSetup()

        #INIT CONTROL SIGNAL SOCKET IF POSSIBLE/DESIRED
        if self.controlstream:
            self._controlStreamSetup()


    def _apply_passed_params(self):
        for p in self.params.keys():
            setattr(self,p,self.params[p])



    def _new_foraging_lap_log(self):
        """
        For imaging_behavior to work, I need a lap variable and terrainlog variable
        It's important to note that the "laps" as defined here won't correspond to the "trials" as above
        Laps will start as soon as a stimulus will shown and will correspond 1:1 with stimuli
        Trials can be aborted if there's a response before a stimulus, so may not contain a stimulus.
        """
        self.laps.append([self.timer.getTime(),self.vsynccount])
        self.terrainlog.append([self.contrast,self.ori])


    def log_trial(self):
        if self.trialvars:
            self.triallog.append(self.trialvars)
        self._new_foraging_lap_log()

    def calculate_next_stim_time(self,now,mean,var):
        next = now + mean + 2*var*np.random.rand()-var
        return next

    def _check_response(self):
        if self.process_response == True:
            if self.stim_on_time:
                latency = self.response_time - self.stim_on_time
            else:
                latency = None
            if latency and latency >= self.response_window[0] and latency <= self.response_window[1] and self.decision == False and self.rewarded==True:
                self.decision = True
                self._process_hit()
            elif latency and latency < self.response_window[0]:
                pass
            elif latency and latency > self.response_window and latency < np.inf and self.decision == False and self.rewarded==True:
                self.decision = True
                self._process_late_response()
            # elif self.vsynccount < self.next_trial_frame:
            #     self.trial_delay() #if we were already delaying the trial, continue to do so
            elif self.decision == False:
                self._process_false_alarm()
            else:
                self.trial_delay()

            self.process_response = False

                    # self._playSound(soundtype='Beep',duration=0.25,volume=0.5)

    def _checkUDP(self):
        """ Checks for UDP command signals. """
        if self.controlstream:
            if self.vsynccount % 10 == 0:
                try:
                    data, addr = self.controlstream.recvfrom(48)
                    if data:
                        data = data.split(' ')
                        self._handleCommand(data)
                except Exception, e:
                    pass

    def _process_hit(self):
        print "HIT AT ",self.timer.getTime()
        print "LATENCY = ",self.timer.getTime()-self.stim_on_time
        print ""
        self.trialvars['response_latency'] = self.timer.getTime()-self.stim_on_time
        if self._reward:
            self._reward(i=self.rewardline) #argument is which spout!
        self.trial_delay()


    def _process_late_response(self):
        print "LATE RESPONSE AT ",self.timer.getTime()
        print "LATENCY = ",self.timer.getTime()-self.stim_on_time
        print ""
        self.trialvars['response_latency'] = self.timer.getTime()-self.stim_on_time
        # self._playSound(soundtype='WhiteNoise',duration=0.2,volume=0.5)
        self.trial_delay()

    def _process_false_alarm(self):
        self.show_stim = False
        print "FALSE ALARM AT ",self.timer.getTime()
        print "LATENCY = ",self.timer.getTime()-self.stim_on_time
        print ""
        self.trialvars['response_latency'] = self.timer.getTime()-self.stim_on_time

        if self.task_mode.lower() == 'testing' or self.task_mode.lower() == 'training':
            # self._playSound(soundtype='WhiteNoise',duration=0.2,volume=0.5)
            print "calling new trial"
            self.abort_on_next_cycle = True
            # self.new_trial()

    def _process_miss(self):
        pass

    def _flip(self):
        if self.syncsqr:
            self.sync.flip(self.vsynccount)
        if self.syncpulse and type(self.syncpulse) is not bool:
            self.syncpulse.WriteBit(self.frameBit, 1)  # set frame bit high
        self.window.flip()  # flips display
        if self.syncpulse and type(self.syncpulse) is not bool:
            self.syncpulse.WriteBit(self.frameBit, 0)  # set frame bit low
        self.vsynccount += 1

        if len(self.window.frameIntervals)>0 and self.window.frameIntervals[-1] > self.window._refreshThreshold:
            self.dropped_frame_count += 1
            if self.dropped_frame_count < self.dropped_frame_threshold:
                print "dropped frame, interval = ",self.window.frameIntervals[-1]



    def display_clock(self,window):
        time = str(round(self.timer.getTime(),3))
        self.clocktext = visual.TextStim(window, text='time   = '+time, wrapWidth = 1500,font='arial',pos=(30,37),alignHoriz='left',color=(1,1,0),height=2.5)
        self.frametext = visual.TextStim(window, text='frame = '+str(self.vsynccount), wrapWidth = 1500,font='arial',pos=(30,40),alignHoriz='left',color=(1,1,0),height=2.5)
        self.clocktext.draw()
        self.frametext.draw()


    def grating_stim(self,window,draw_central,ori=0,contrast=1,color=1,phase=0.25):
        # self.grating.setOri(ori)
        # self.grating.setContrast(contrast)
        # print "CURRENT ORIS",self.current_oris
        if draw_central==True:
            for i,grating in enumerate(self.grating):
                self.grating[i].setOri(ori)
                self.grating[i].setContrast(contrast)
                self.grating[i].setColor(color)
                self.grating[i].setPhase(phase)
                self.grating[i].draw()


    def image_stim(self,window,method_type='ImageStimNumpyuByte'):

        # self.image.setImage(self.image_path)
        if method_type.lower() == 'imagestimnumpyubyte':
            """ This use's Jay Borseth's custom image method"""
            self.image.setReplaceImage(self.image_arr)
            self.image.setContrast(self.contrast)
            self.image.setPos(self.pos)
        elif method_type == 'imagestim':
            """ This is the standard psychopy method """
            self.image.setImage(self.image_paths[self.image_index])
            self.image.setSize(self.size)
            self.image.setOri(self.ori)
            self.image.setPos(self.pos)

        self.image.draw()


    def background(self,window):
        self.bgstim.draw()

    def blankScreen(self,window):
        self.blank.draw()

    def fullScreenPlaid(self,window):
        self.plaid1.draw()
        self.plaid2.draw()

    def _check_keys(self):
        """Checks key input"""
        for keys in event.getKeys(timeStamped=True):
            self.keylog.append({'eventlog':keys,'experiment_time:':self.timer.getTime()})
            # self.trialvars['response_type'].append((keys[0]))
            # self.trialvars['response_time'].append(self.timer.getTime())
            # self.responselog.append({'time':self.timer.getTime(),'frame':self.vsynccount,'type':keys[0]})
            if keys[0] in ['t']:
                print "current time in experiment is: ",self.timer.getTime()
            elif keys[0] in ['escape', 'q']:
                self.active = False
            elif keys[0] in ['p']:
                if self.paused == True:
                    self.paused = False
                else:
                    self.paused = True
            elif keys[0] in ['left']:
                self.left_response_time = self.timer.getTime()
                self.process_response = True
            elif keys[0] in ['right']:
                self.right_response_time = self.timer.getTime()
                self.process_response = True
            elif keys[0] in ['space','right','left']:
                self.response_time = self.timer.getTime()
                self.process_response = True
                # self.next_trial_time = self.calculate_next_stim_time(self.timer.getTime(),self.ISI_mean,self.ISI_var)

    def _playSound(self,soundtype='WhiteNoise',duration=0.5,volume=0.05,toggle_to=True):
        self.auditory_stimulus_log.append({'time':self.timer.getTime(), 'frame':self.vsynccount,'state':toggle_to,'duration':duration,'volume':volume,'soundtype':soundtype})
        if soundtype=='WhiteNoise':
            if toggle_to == True:
                WN_Length = duration
                randomarray=np.array([2*np.random.random()-1 for i in xrange(int(round(44100*WN_Length)))])
                self.wn_sound = sound.Sound(value = randomarray)
                self.wn_sound.setVolume(volume)
                self.wn_sound.play()
            elif toggle_to == False:
                self.wn_sound.stop()
        if soundtype == 'Beep':
            # print "!!!!!!!!!!!!!!!!!!!!!!!!BEEP!!!!!!!!!!!!!!!!!!!!!!"
            tone = sound.Sound(value='C', sampleRate=44100, secs=duration, bits=8, octave=5)
            tone.setVolume(volume)
            tone.play()


    def _finalize(self):
        """ Stops some clocks ASAP. """
        #STOP CLOCKS
        # self.window.setRecordFrameIntervals(False)  # stop recording frame intervals
        self.active = False
        if not self.stoptime:

            self.stoptime = self.timer.getTime()  # TIME SENSITIVE STUFF ENDS HERE


            #Close display window
            self.window.close()

            timestr = str(datetime.timedelta(seconds=(self.stoptime-self.starttime)))
            print "self.starttime:",self.starttime
            print "self.stoptime:",self.stoptime
            print "Actual experiment duration:", timestr
            self.stopdatetime = datetime.datetime.now()
            self._cleanup()
            self._conditionData()
            self._logMeta()

    def _cleanup(self):
        print "in cleanup"
        #CLOSE NIDAQ TASKS
        #CLOSE EVERYTHING
        if self.syncpulse and self.syncpulse is not "False":
            self.syncpulse.WriteBit(self.sweepBit, 0)  # ensure sweep bit is low
            self.syncpulse.WriteBit(self.frameBit, 0)  # ensure frame bit is low
        try:
            if self.do:
                self.do.ClearTask()
                self.do = None
        except Exception, e:
            print "Error closing DO task:", e
        try:
            if self.di:
                self.di.ClearTask()
                self.di = None
        except Exception, e:
            print "Error closing DI task:", e
        try:
            if self.ao:
                self.ao.ClearTask()
                self.ao = None
        except Exception, e:
            print "Error closing AO task:", e
        try:
            if self.ai:
                self.ai.ClearTask()
                self.ai = None
        except Exception, e:
            print "Error closing AI task:", e
        try:
            if self.datastream:
                self.datastream.close()
        except Exception, e:
            print "Error closing data stream:", e

        try:
            if self.licksensor:
                self.licksensor.ClearTask()
                self.licksensor = None
        except Exception, e:
            print "Error closing licksensor task:", e

        try:
            if self.timer:
                self.timer = None
        except Exception, e:
            print "Error clearing timer task"

        #Stop eyetracker if it exists
        print "STOPPING EYE TRACKER"
        if self.eyetracker:
            self.eyetracker.recordStop()

        self.vsyncintervals = 1000*np.array(self.window.frameIntervals)




    def _conditionData(self):
        """Gets some data ready for storage."""
        self.monitor = getMonitorInfo(self.window.monitor)
        self.platform = getPlatformInfo()
        self.startdatetime = str(self.startdatetime)
        self.stopdatetime = str(self.stopdatetime)
        #Delete Psychopy Objects because we don't want to have to worry about
        # users needing Psychopy to unpickle.  Maybe make them strings instead?
        try:
            self.grating = str(self.grating)
            self.blank = str(self.blank)
        except:
            pass


        if self.syncsqr:
            self.sync = str(self.sync)
        self.window = str(self.window)
        self.keys = False
        if self.syncpulse:
            self.syncpulse = 'True'
        else:
            self.syncpulse = 'False'
        if self.eyetracker:
            self.eyetracker = str(self.eyetracker)

        self.rewards = np.array(self.rewards)
        self.airpuffs = np.array(self.airpuffs)
        self.vin = np.array(self.vin, dtype=np.float16)
        self.vsig = np.array(self.vsig, dtype=np.float16)
        self.laps = np.array(self.laps)
        self.lickData = np.where(np.array(self.lickData, dtype=np.uint8) > 0)

    def _logMeta(self):
        """ Writes all important information to log. """
        mouseid = self.mouseid
        directory = os.path.join(self.logdir, mouseid+"/output")
        filename = "task="+self.task+"_stage="+str(self.stage)+"_mouse="+mouseid

        if hasattr(self, 'filenamesuffix'):
            if self.filenamesuffix:
                filename = filename + '-' + self.filenamesuffix

        log = logger(directory, filename, genmatfile=False)
        if self.backupdir:
            log.backupFileDir = os.path.join(self.backupdir, mouseid+"/output")
        output = wecanpicklethat(self.__dict__)
        output = self.remove_unidentified_objects(output)
        print "Unpickleable:", output['unpickleable']
        log.add(**output)
        log.close()
        self.picklepath = log.picklepath


    def remove_unidentified_objects(self,data):
        """
        this will remove any objects that aren't standard python objects
        Derric's "wecanpicklethat" is missing some objects that interfere with our ability to open the files

        This will check each object in the data dictionary against a known list of safely pickleable object types
        If it doesn't match any of the known types, it gets set to None
        """
        for key in data.keys():
            obj = data[key]
            if isinstance(obj, str):
                pass
            elif isinstance(obj, basestring):
                pass
            elif isinstance(obj, (int, long, float, complex)):
                pass
            elif isinstance(obj, (tuple, list, dict, set)):
                pass
            elif isinstance(obj, np.ndarray):
                pass
            elif obj is None:
                pass
            else:
                print "removed " + key + " from data dictionary before pickling - Unknown type"
                data[key] = None
        return data

    def _dataStreamSetup(self):
        """ Sets up data output stream. """
        try:
            self._readconfig("Datastream", override=self.params)
            print "Streaming to:", self.performanceip, self.performanceport
            self.datastream = DataStream(ip=self.performanceip,
                                         port=self.performanceport)
            #Send header
            data = {}
            data = self.__dict__.copy()
            data['terrain'] = {}
            # # the online analysis GUI freezes up if the lapdistance is too large. This prevents that problem.
            # if data['terrain']['lapdistance'] > 10000:
            #     temp = data['terrain']['lapdistance']
            #     data['terrain']['lapdistance'] = 300
            #     self.datastream.transmit(data)
            #     data['terrain']['lapdistance'] = temp
            # else:
            self.datastream.transmit(data)
            #INIT DATA TO BE SENT TO PERFORMANCE TRACKER
            self.lapdata = {'reward': [], 'object': None,
                            'laptime': None, 'posx': None,
                            'iscorrect': None, 'lickdata': None,
                            'commands': []}
        except Exception, e:
            print "Could not connect to performance tracker.", e
            self.datastream = None

    def _setupDAQ(self):
        """ Sets up some digital IO for sync and tiggering. """
        try:
            if self.invertdo:
                istate = 'low'
            else:
                istate = 'high'
            self.do = DigitalOutput(self.nidevice, self.doport,
                                    initial_state=istate)
            self.do.StartTask()
        except Exception, e:
            print "Error starting DigitalOutput task:", e
            self.do = None
        try:
            self.di = DigitalInput(self.nidevice, self.diport)
            self.di.StartTask()
        except Exception, e:
            print "Error starting DigitalInput task:", e
            self.di = None
        try:
            #set up 8 channels, only use 2 though for now
            self.ai = AnalogInput(self.nidevice, range(8), buffer_size=25,
                                  clock_speed=6000.0)
            self.ai.StartTask()
        except Exception, e:
            print "Error starting AnalogInput task:", e
            self.ai = None

        try:
            self.ao = AnalogOutput(self.nidevice, channels=[0, 1],
                                   voltage_range=[0.0, 5.0])
            self.ao.StartTask()
        except Exception, e:
            print "Error starting AnalogOutput task:", e
            self.ao = None


    def _syncpulseSetup(self):
        """ Sets up a Digital IO sync pulse. """
        try:
            self.syncpulse = self.do
            self.sweepBit = self.syncpulselines[0]
            self.frameBit = self.syncpulselines[1]
            if len(self.syncpulselines) > 2:
                self.syncsqrBit = self.syncpulselines[2]
            self.syncpulse.WriteBit(self.sweepBit, 0)  # ensure sweep bit is low
            self.syncpulse.WriteBit(self.frameBit, 0)  # ensure frame bit is low
        except Exception, e:
            self.syncpulse = False
            warn("Failed to set up syncpulse: {}".format(e))

    def _eyetrackerSetup(self):
        """ Sets up an eyetracker UDP Client. """
        try:
            from aibs.Eyetracking.EyetrackerClient import Client
            self.eyetracker = Client(outgoing_ip=self.eyetrackerip,
                                     outgoing_port=self.eyetrackerport,
                                     output_filename=self.moviefilename)
            self.eyetracker.setup()
            self.eyedatalog = []
            if self.trackeyepos:
                self._eyeinitpos = None
            print "///////////////////"
            print "in eyetracker setup"
            print
        except Exception, e:
            print "Could not initialize eyetracker:", e
            self.eyetracker = None

    def _encoderSetup(self):
        """ Attempts to set up encoder NI task. """
        try:
            from aibs.Encoder import Encoder
            self.encoder = Encoder(device=self.nidevice,
                vin=self.encodervinchannel,
                vsig=self.encodervsigchannel,
                task=self.ai)
            time.sleep(0.1)  # wait for first data buffer
            self._encDeg = self.encoder.getDegrees()  # get initial state
            if not self._encDeg:
                self._encDeg = 0  # ?????????
        except Exception, e:
            print "Could not initialize Encoder.  Ensure that NIDAQ is connected properly.", e
            self._encDeg = 0
            self.encoder = None
            print "Switching to key control..."
            self.keys = key.KeyStateHandler()
            self.window.winHandle.push_handlers(self.keys)

    def _rewardSetup(self):
        """ Gets reward calibration from file and sets up reward objects. """
        try:
            configfolder = self._getConfigFolder()
            volumecalfile = os.path.join(configfolder, 'volume.cfg')
            with open(volumecalfile) as f:
                calibration = [eval(line) if line.rstrip('\n') else None for line in f.readlines()] #modified by chris 9/2/2014
            print "Volume calibration Vals: ",calibration
        except Exception, e:
            print "Error reading volume calibration file, using default calibration.", e
            calibration = (1, 0)
        try:
            self._readconfig("Reward", override=self.params)
            from aibs.Reward import Reward
            if self.lickports != len(self.rewardlines):
                raise IndexError("There should be a reward line for each lick port!")
            self.reward = []
            for i in range(self.lickports):
                self.reward.append(Reward(port=self.rewardport,
                    line=self.rewardlines[i], rewardvol=self.rewardvol,
                    calibration=calibration[self.rewardlines[i]], mode='volume', #modified by chris 9/2/2014
                    task=self.do, invert=self.invertdo))
            #print str(self.reward)
        except Exception, e:
            print "Could not initialize Reward.  Ensure that NIDAQ is connected properly.", e
            self.reward = None

    def _airpuffSetup(self):
        """ Sets up a airpuffs as aversive stimuli on the digital output task. """
        try:
            from aibs.Reward import Punishment
            self._readconfig("Punishment",override=self.params)
            self.airpuff = Punishment(line=self.airpuffline,task=self.do,
                invert=self.invertdo,punishtime=0.05)
        except Exception, e:
            print "Could not initialize Airpuffs:", e
            self.airpuff = None

    def _readconfig(self, section, override={}):
        """ Reads the config file for the specified section. """
        config = getConfig(section, 'stim.cfg')
        for k in override.keys():
            if k in config.keys():
                config[k] = override[k]
        for k, v in config.iteritems():
            setattr(self, k.lower(), v)

    def _getConfigFolder(self):
        aibstimfolder = getdirectories()
        configfolder = os.path.join(aibstimfolder, 'config')
        checkDirs(configfolder)
        return configfolder

    def _lickSensorSetup(self):
        """ Attempts to set up lick sensor NI task. """
        ##TODO: Make lick sensor object if necessary. Let user select port and line.
        print "Attempting to set up lick sensor"
        print "======================================"
        if self.di:
            self.lickSensor = self.di  # just use DI for now
            licktest = []
            for i in range(30):
                licktest.append(self.di.Read()[self.rewardlines[0]])
                time.sleep(0.01)
            licktest = np.array(licktest, dtype=np.uint8)
            if len(licktest[np.where(licktest > 0)]) > 25:
                self.lickSensor = None
                self.lickData = [np.zeros(len(self.rewardlines))]
                print "Lick sensor failed startup test."
        else:
            print "Could not initialize lick sensor.  Ensure that NIDAQ is connected properly."
            print "======================================"
            self.keycontrol = True
            self.lickSensor = None
            self.lickData = [np.zeros(len(self.rewardlines))]
            self.keys = key.KeyStateHandler()
            self.window.winHandle.push_handlers(self.keys)

    def _checkLickSensor(self):
        """ Checks to see if a lick is occurring. """
        ##TODO: Let user select line for lick sensing.
        if self.lickSensor:
            data = self.lickSensor.Read()[self.rewardlines]
            self.lickData.append(data)
        elif self.keycontrol == True: #NO NI BOARD.  KEY INPUT?
            if self.keys[key.SPACE]:
                data = [1,0]
            elif self.keys[key.NUM_1]:
                data = [1,0]
            elif self.keys[key.NUM_3]:
                data = [0,1]
            else:
                data = [0,0]
            self.lickData.append(data)

        if self.lickSensor and int(1 in self.lickData[-1]):
            self.trialvars['lick_times'].append(self.timer.getTime())
            self.response_time = self.timer.getTime()
            self.responselog.append({'time':self.timer.getTime(),'frame':self.vsynccount,'type':data})
            self.process_response = True
            # self.next_trial_time = self.calculate_next_stim_time(self.timer.getTime(),self.ISI_mean,self.ISI_var)

    def _checkEncoder(self):
        """ Checks encoder values and tweaks foreground object position based on speedgain. """
        if self.encoder:
            vin = self.encoder.getVin()
            vsig = self.encoder.getVsig()
            self.vin.append(vin)
            self.vsig.append(vsig)
            deg = self.encoder.getDegrees()
            if (6 > vin > 4) & (deg is not None):  # weird NIDAQ errors requires this check
                dx = deg-self._encDeg
                self._encDeg = deg
            else:
                dx = self._lastDx
                self._encDeg += dx
            self._lastDx = dx

        else:  # NO NI BOARD.  Log nans
            self.vin.append(np.nan)
            self.vsig.append(np.nan)
            self._lastDx = np.nan

        self.dx.append(self._lastDx)

    def _reward(self, i=0):
        """ Issues a reward to the animal on reward line i (default is 0) """
        t = self.timer.getTime()
        self.rewards.append((t, self.vsynccount, i))
        if self.play_sounds == True:
            self._playSound(soundtype='Beep',duration=0.2,volume=1)
        if self.reward:
            self.reward[i].reward()
        else:
            print("Reward! at %s" % t)
            print "Number of rewards so far:",len(self.rewards)

        if self.datastream:
            self.lapdata['reward'].append((t, self.vsynccount, i))
        self.trialvars['reward_times'].append(self.timer.getTime())
        self.trialvars['reward_frames'].append(self.vsynccount)

    def _airpuff(self, i=1):
        """ Toggles the solenoid on line i (default is 1) to deliver an air puff """
        t = self.timer.getTime()
        if self.airpuff:
            self.airpuff.punish()
        else:
            print("Airpuff! at %s" % t)
        self.airpuffs.append((t, self.vsynccount))
        self.trialvars['airpuff_times'].append(self.timer.getTime())
        self.trialvars['airpuff_frames'].append(self.vsynccount)

    def _controlStreamSetup(self):
        """ Sets up control steam socket to receive commands from GUI. """
        try:
            self.controlstream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.controlstream.bind((AGENT_IP, AGENT_PORT))
            self.controlstream.settimeout(0.0)
        except Exception, e:
            print "Failed to set up control stream:", e
            self.controlstream = None

    def _handleCommand(self, command):
        """ Handles a command from a UDP source. """

        if command[0] == 'SET':
            try:
                name = command[1].split('.')
                newvalue = eval(command[2])
                if len(name,) == 2:
                    oldvalue = getattr(eval("self."+name[0]), name[1])
                    if type(oldvalue) == type(newvalue):
                        setattr(eval("self."+name[0]), name[1], newvalue)  # value is in child object
                    else:
                        try:
                            oldtype = type(oldvalue)  # cast as new type?
                            newvalue = oldtype(newvalue)
                            setattr(eval("self."+name[0]), name[1], newvalue)  # value is in child object
                        except:
                            raise TypeError('Old value is %s, new value is %s' % (
                                type(oldvalue), type(newvalue)))
                elif len(name,) == 1:
                    oldvalue = getattr(self, name[0])
                    if type(oldvalue) == type(newvalue):
                        setattr(self, name[0], newvalue)  # value is in self
                    else:
                        try:
                            oldtype = type(oldvalue)
                            newvalue = oldtype(newvalue)
                            setattr(self, name[0], newvalue)
                        except:
                            raise TypeError('Old value is %s, new value is %s' % (
                                type(oldvalue), type(newvalue)))
                elif len(name,) > 2:
                    raise ValueError('Command could not be parsed. Check formatting.')
                commandlist = (command[1], oldvalue, newvalue, self.vsynccount)
                self.commandrecord.append(commandlist)
                print commandlist
            except Exception, e:
                print "Failed to set value:", e

        elif command[0] == 'GET':
            ##TODO: Do something with value that we get...
            try:
                name = command[1].split('.')
                if len(name,) == 2:
                    value = getattr(eval("self."+name[0]), name[1])
                elif len(name,) == 1:
                    value = getattr(self, name[0])
            except Exception, e:
                print "Failed to get value:", e

        elif command[0] == 'RUN':
            try:
                methodname = command[1]  # currently only works with no args
                getattr(self, methodname)()
                commandlist = (command[1], self.vsynccount)
                self.commandrecord.append(commandlist)
                print commandlist
            except Exception, e:
                print "Failed to run method:", e

        else:
            print "Couldn't parse received command:", command


if __name__ == '__main__':
    mon = monitors.Monitor('testMonitor')#fetch the most recent calib for this monitor
    mon.setDistance(15)
    window = visual.Window(monitor=mon, units="deg",fullscr = False,size=(200,200),screen =0,allowGUI=False)
    window.setMouseVisible(False)
    params = {'domain':'time'}
    stim = Stim(window=window,params=params)
    stim.run(duration= 10*60)
    print ""
    print "min frame interval:",np.min(stim.vsyncintervals)
    print "max run clock interval:",np.max(stim.vsyncintervals)
    print "mean frame intervals:",np.mean(stim.vsyncintervals)
