import random
import os
import numpy as np
import random

from psychopy import visual, core, event, monitors
from psychopy.hardware import keyboard
from psychopy.visual import textbox


class Screen:
    def __init__(self, CONF):
        self.CONF = CONF

        # fetch the most recent calib for this monitor
        mon = monitors.Monitor('tesfgft')
        mon.setWidth(CONF["screen"]["size"][0])
        mon.setSizePix(CONF["screen"]["resolution"])

        self.window = visual.Window(
            size=CONF["screen"]["resolution"],
            color=CONF["pause"]["backgroundColor"],
            # display_resolution=CONF["screen"]["resolution"],
            monitor=mon,
            fullscr=CONF["screen"]["full"],
            allowGUI=True,
            units="cm"
        )

        # set up instructions and overview
        self.task = visual.TextStim(self.window,
                                    # pos=[0, 0],
                                    text=CONF["task"]["name"],
                                    alignHoriz='center',
                                    alignVert='center',
                                    height=.3,
                                    pos=(0, 0),  # TEMP
                                    units="norm"
                                    # units="cm"
                                    )
        self.session = visual.TextStim(self.window,
                                       text="P" + CONF["participant"] +
                                       " Session " + CONF["session"],
                                       pos=[.75, -.3],  # TEMP
                                       height=.1,
                                       alignHoriz='center',
                                       alignVert='center',
                                       units="norm"
                                       )

        self.instructions = visual.TextStim(
            self.window, text=CONF["instructions"]["text"], height=.05)

        self.startPrompt = visual.TextStim(
            self.window, text=CONF["instructions"]["startPrompt"], height=0.05, pos=[0, -.3])

        self.cue = visual.TextStim(self.window)

        ###############
        # setup stimuli
        # self.symbol = visual.ImageStim(
        #     self.window,
        #     units="cm",
        #     height=CONF["stimuli"]["stimHeight"]
        # )

        # self.fixation = visual.TextStim(
        #     self.window,
        #     text="+",
        #     pos=[0, 0],
        #     height=2
        # )
        # set up instructions and overview
        # self.fixation = visual.TextStim(self.window,
        #                                 # pos=[0, 0],
        #                                 text="+",
        #                                 alignHoriz='center',
        #                                 alignVert='center',
        #                                 pos=(0, 0),  # TEMP
        #                                 )
        self.fixation = visual.Rect(
            self.window,
            pos=[0, 0],
            height=2,
            width=2
        )

        # find the center position of all cells in the grid

        def findPosition(n, l):
            return (n-1)*l/2

        # half the total distance from first to last position on the x axis
        halfx = findPosition(
            self.CONF["stimuli"]["gridDimentions"][1], self.CONF["stimuli"]["cellHeight"])
        halfy = findPosition(
            self.CONF["stimuli"]["gridDimentions"][0], self.CONF["stimuli"]["cellHeight"])

        x = np.linspace(-halfx, halfx,
                        self.CONF["stimuli"]["gridDimentions"][1])
        y = np.linspace(-halfy, halfy,
                        self.CONF["stimuli"]["gridDimentions"][0])

        self.x = np.concatenate((x, x))
        self.y = np.repeat(y, len(x))

        # get list of filenames
        self.files = os.listdir(CONF["stimuli"]["location"])

    def show_overview(self):
        self.task.draw()
        self.session.draw()
        self.window.flip()

    def show_instructions(self):
        self.instructions.draw()
        self.startPrompt.draw()
        self.window.flip()

    def show_blank(self):
        self.window.flip()

    def show_cue(self, word):
        self.cue.setText(word)
        self.cue.draw()
        self.window.flip()

    def _draw_symbol(self, idx, color):
        self.fixation.color = color
        self.fixation.pos = [self.x[idx], self.y[idx]]
        self.fixation.draw()
        # self.symbol.setImage(filepath)

    def show_new_grid(self, level):
        stimuli = []
        # symbolFiles = random.sample(self.files, level)
        # xLocation = random.sample(
        #     range(self.CONF["stimuli"]["gridDimentions"][1]), 1)

        # for filename in symbolFiles:
        for idx in range(len(self.x)):

            # path = os.path.join(self.CONF["stimuli"]["location"], filename)
            print(idx)
            self._draw_symbol(idx, "white")
        # stimuli.append({"file": filename})
        # idx += idx

        self.window.flip()
        print("flipped")
        return stimuli
