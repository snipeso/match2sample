import random
import os
import numpy as np
import random

from psychopy import visual, core, event, monitors
from psychopy.hardware import keyboard
from psychopy.visual import textbox

from config.configMatch2Sample import CONF

# fetch the most recent calib for this monitor
mon = monitors.Monitor('tesfgft')
mon.setWidth(CONF["screen"]["size"][0])
mon.setSizePix(CONF["screen"]["resolution"])

window = visual.Window(
    size=CONF["screen"]["resolution"],
    color=CONF["pause"]["backgroundColor"],
    # display_resolution=CONF["screen"]["resolution"],
    monitor=mon,
    fullscr=False,
    allowGUI=True,
    units="cm"
)

# set up instructions and overview
task = visual.ImageStim(window, image="stimuli/aa.png")

task.draw()
window.flip()
core.wait(3)
