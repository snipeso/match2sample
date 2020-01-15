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
            color=CONF["fixation"]["colorOff"],
            # display_resolution=CONF["screen"]["resolution"],
            monitor=mon,
            fullscr=CONF["screen"]["full"],
            # units="cm",
            allowGUI=True
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

        # Setup background
        self.fixation_box = visual.Rect(
            self.window, height=CONF["fixation"]["height"],
            width=CONF["fixation"]["width"],
            fillColor=CONF["fixation"]["boxColor"],
            lineColor=CONF["fixation"]["boxColor"],
            units=CONF["screen"]["units"])

        self.left_on = visual.Rect(
            self.window, height=2,
            width=1,
            pos=(-.5, 0),
            fillColor=CONF["fixation"]["colorOn"],
            lineColor=CONF["fixation"]["colorOn"],
            units="norm")

        self.right_on = visual.Rect(
            self.window, height=2,
            width=1,
            pos=(.5, 0),
            fillColor=CONF["fixation"]["colorOn"],
            lineColor=CONF["fixation"]["colorOn"],
            units="norm")

        self.rightBorder = CONF["screen"]["size"][0] / \
            2  # TODO: move to screen
        self.topBorder = CONF["screen"]["size"][1] / 2

        # setup stimuli
        self.spot = visual.Circle(
            self.window,
            edges=100,
            units="cm"
        )

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

    def set_background(self, showLeft):
        if showLeft:
            self.backgroundLeft = True
        else:
            self.backgroundLeft = False

        self.show_background()

    def generate_coordinates(self):
        if self.backgroundLeft:
            x = random.uniform(-self.rightBorder + self.CONF["task"]["maxRadius"],
                               0 - self.CONF["task"]["maxRadius"])
        else:
            x = random.uniform(
                0 + self.CONF["task"]["maxRadius"], self.rightBorder - self.CONF["task"]["maxRadius"])

        self.x = x
        self.y = random.uniform(-self.topBorder + self.CONF["task"]["maxRadius"],
                                self.topBorder - self.CONF["task"]["maxRadius"])
        return [self.x, self.y]

    def flash_fixation_box(self):
        self._flip_fixation_color(self.CONF["task"]["earlyColor"])
        core.wait(self.CONF["fixation"]["errorFlash"])
        self._flip_fixation_color(self.CONF["fixation"]["boxColor"])

    def start_spot(self):
        self.spot.pos = [self.x, self.y]
        # TODO: make centimeter thing work, and depend on screen size
        self.spot.radius = self.CONF["task"]["maxRadius"]
        self._set_spot_color(self.CONF["task"]["color"])
        self._draw_background()
        self.spot.draw()
        self.window.flip()

    def shrink_spot(self, size, colored=False):
        self.spot.radius = self.CONF["task"]["maxRadius"]*size

        self._draw_background()
        self.spot.draw()
        self.window.flip()

    def _set_spot_color(self, color):
        self.spot.fillColor = color
        self.spot.lineColor = color

    def _flip_fixation_color(self, color):
        self.fixation_box.fillColor = color
        self.fixation_box.lineColor = color
        self._draw_background()
        self.fixation_box.draw()
        self.window.flip()

    def show_background(self):
        self._draw_background()
        self.window.flip()

    def _draw_background(self):
        if self.backgroundLeft:
            self.left_on.draw()
        else:
            self.right_on.draw()
        self.fixation_box.draw()

    def show_result(self, time):
        # gives different color stimulus depending on result
        radiusPercent = (self.CONF["task"]["maxTime"] -
                         time) / self.CONF["task"]["maxTime"]
        if time < self.CONF["task"]["minTime"]:
            self.flash_fixation_box()
            return
        elif time < self.CONF["task"]["maxTime"]:
            self._set_spot_color(self.CONF["task"]["victoryColor"])
        else:
            return

        self.shrink_spot(radiusPercent)
