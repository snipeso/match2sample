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
        self.symbol = visual.ImageStim(
            self.window,
            size=(CONF["stimuli"]["stimHeight"], CONF["stimuli"]["stimHeight"])
        )

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
            height=.5,
            width=.5,
            units="cm",
            color="red"
        )

        ###################################################
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
        # cartesian product to get all coordinate combos
        coordinates = [(xx, yy) for xx in x for yy in y]

        midpointIndx = len(coordinates) // 2
        self.midpoint = coordinates[midpointIndx]
        del coordinates[midpointIndx]
        self.coordinates = coordinates

        # get list of filenames
        # TODO: make this already include the path
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

    def show_fixation(self):
        self.fixation.draw()
        self.window.flip()

    def show_cue(self, word):
        self.cue.setText(word)
        self.cue.draw()
        self.window.flip()

    def _draw_symbol(self, filename, location):
        filepath = os.path.join(
            self.CONF["stimuli"]["location"], filename)

        if location is not None:
            self.symbol.pos = location

        else:
            self.symbol.pos = self.midpoint
            print("0", self.symbol.pos)
        self.symbol.setImage(filepath)
        self.symbol.draw()

    def show_new_grid(self, level):
        stimuli = {}
        symbolFiles = random.sample(self.files, level)
        locations = random.sample(
            self.coordinates, level)
        print("all locs", locations)

        for idx, filename in enumerate(symbolFiles):
            self._draw_symbol(filename, locations[idx])

        stimuli["filenames"] = symbolFiles
        stimuli["locations"] = locations

        self.fixation.draw()
        self.window.flip()

        self.stimuli = stimuli

    def show_probe(self, filename):
        self._draw_symbol(filename, None)
        self.window.flip()
