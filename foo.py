from psychopy import visual, event
from memory_util import total_size

window = visual.Window(size=(100, 100))
time = "10"

clocktext = visual.TextStim(window, text='time   = '+time, wrapWidth = 1500,font='arial',pos=(30,37),alignHoriz='left',color=(1,1,0),height=2.5)
frametext = visual.TextStim(window, text='frame = '+str(10), wrapWidth = 1500,font='arial',pos=(30,40),alignHoriz='left',color=(1,1,0),height=2.5)

print total_size(clocktext)
print total_size(frametext)
