import logging
import os
import random
import time
import sys
# import psychtoolbox as ptb

from chronometer import Chronometer
from screen import Screen
from scorer import Scorer
from psychopy import core, event, sound
from psychopy.hardware import keyboard

from datalog import Datalog
from config.configHemiPVT import CONF

#########################################################################

# Initialize screen, logger and inputs
logging.basicConfig(
    level=CONF["loggingLevel"],
    format='%(asctime)s-%(levelname)s-%(message)s',
)  # This is a log for debugging the script, and prints messages to the terminal

screen = Screen(CONF)
scorer = Scorer()
datalog = Datalog(OUTPUT_FOLDER=os.path.join(
    'output', CONF["task"]["name"]), CONF=CONF)  # This is for saving data
kb = keyboard.Keyboard()
mainClock = core.MonotonicClock()  # starts clock for timestamping events
alarm = sound.Sound(os.path.join('sounds', CONF["tones"]["alarm"]),
                    stereo=True)

# Experiment conditions
showLeft = random.choice([True, False])


logging.info('Initialization completed')

#########################################################################


def quitExperimentIf(shouldQuit):
    "Quit experiment if condition is met"

    if shouldQuit:
        scorer.getScore()
        logging.info('quit experiment')
        sys.exit(2)  # TODO: make version where quit is sys 1 vs sys 2


def onFlip():  # TODO: does this go somewhere else?
    kb.clock.reset()  # this starts the keyboard clock as soon as stimulus appears
    datalog["startTime"] = mainClock.getTime()
    # TODO: send start trigger

##############
# Introduction
##############


# Display overview of session
screen.show_overview()
core.wait(CONF["timing"]["overview"])

# Optionally, display instructions
if CONF["showInstructions"]:
    screen.show_instructions()
    key = event.waitKeys()
    quitExperimentIf(key[0] == 'q')

# Blank screen for initial rest
screen.show_blank()
logging.info('Starting blank period')

# TODO: send start trigger
core.wait(CONF["timing"]["rest"])
# TODO: send end wait trigger

# Cue start of the experiment
screen.show_cue("START")
core.wait(CONF["timing"]["cue"])

##########################################################################

#################
# Main experiment
#################

# initialize variables
stimulus_number = 0
totBlocks = CONF["task"]["blocks"]


################################################
# loop through blocks, switching side every time
for block in range(1, totBlocks + 1):

    # set counter
    totMissed = 0

    # set hemifield
    showLeft = not showLeft  # switches visual field
    screen.set_background(showLeft)

    logging.info(f"{block} / {totBlocks}")

    # start block
    blockTimer = core.CountdownTimer(CONF["task"]["duration"])
    while blockTimer.getTime() > 0:
        stimulus_number += 1
        logging.info('Starting iteration #%s with leftOn=#%s',
                     stimulus_number, showLeft)

        ###############################
        # Wait a random period of time

        # create delay for wait
        delay = random.uniform(
            CONF["fixation"]["minDelay"],
            CONF["fixation"]["maxDelay"]) - CONF["task"]["extraTime"]  # the extra time delay happens after stimulus presentation

        logging.info('Starting delay of %s seconds', delay)

        # start delay
        delayTimer = core.CountdownTimer(delay)

        extraKeys = []
        tones = []
        while delayTimer.getTime() > 0:

            # play randomly tones in the mean time
            tone = sound.Sound(os.path.join(
                "sounds", CONF["tones"]["tone"]), volume=CONF["tones"]["volume"])

            toneDelay = random.uniform(
                CONF["tones"]["minTime"], CONF["tones"]["maxTime"])

            toneTimer = core.CountdownTimer(toneDelay)
            logging.info("tone delay of %s", toneDelay)
            while delayTimer.getTime() > 0 and toneTimer.getTime() > 0:

                #  Record any extra key presses during wait
                key = kb.getKeys()
                if key:
                    # TODO: make seperate function that also keeps track of q, make q in config
                    quitExperimentIf(key[0].name == 'q')

                    extraKeys.append(mainClock.getTime())

                    # Flash the fixation box to indicate unexpected key press
                    screen.flash_fixation_box()

            # don't play sound if there's less time left than the tone's duration
            if delayTimer.getTime() < 0.05:
                continue

            # play tone on next flip TODO: see if this is ok
            nextFlip = screen.window.getFutureFlipTime(clock='ptb')
            tone.play(when=nextFlip)
            # screen.flash_fixation_box()

            # log
            tones.append(mainClock.getTime())  # TODO, make this happen on flip
            logging.info("tone at %s", mainClock.getTime())

        # log data
        datalog["hemifield"] = "left" if showLeft else "right"
        datalog["block"] = block
        datalog["sequence_number"] = stimulus_number
        datalog["delay"] = delay
        datalog["tones"] = tones
        datalog["extrakeypresses"] = extraKeys
        scorer.scores["extraKeys"] += len(extraKeys)

        core.wait(CONF["task"]["extraTime"])

        #######################
        # Stimulus presentation

        # create new x and y
        coordinates = screen.generate_coordinates()
        datalog["coordinates"] = coordinates

        # initialize stopwatch
        missed = False
        late = False

        # run stopwatch
        logging.info("waiting for shrinking to start")
        timer = core.CountdownTimer(CONF["task"]["maxTime"])
        screen.window.callOnFlip(onFlip)

        screen.start_spot()
        keys = []

        while not keys:
            keys = kb.getKeys(waitRelease=False)
            now = timer.getTime()

            if now <= -CONF["task"]["extraTime"]:  # stop waiting for keys
                missed = True
                break
            elif now <= 0:  # keep waiting for keys, but don't show stimulus
                late = True
                radiusPercent = 0
            else:  # shrink stimulus
                radiusPercent = now/CONF["task"]["maxTime"]

            screen.shrink_spot(radiusPercent)
        # TODO: response trigger

        #########
        # Outcome

        if missed:
            logging.info("missed")
            datalog["missed"] = True
            scorer.scores["missed"] += 1
            totMissed += 1

            # raise alarm if too many stimuli missed
            logging.warning("Missed: %s", totMissed)
            if totMissed > CONF["task"]["maxMissed"]:
                # TODO: sound alarm
                alarm.play()
                datalog["alarm"] = mainClock.getTime()
                logging.warning("alarm sound!!!!!")

        else:
            # show result
            reactionTime = keys[0].rt
            logging.info('RT: %s', reactionTime)
            screen.show_result(reactionTime)
            core.wait(CONF["fixation"]["scoreTime"])
            screen.show_background()

            # exit if asked
            quitExperimentIf(keys[0].name == 'q')

            # reset missed count
            totMissed = 0

            # save to memory
            datalog["rt"] = reactionTime
            datalog["response_key"] = keys[0].name

            if reactionTime > CONF["task"]["minTime"]:
                scorer.newRT(reactionTime)
                if late:
                    datalog["late"] = True
                    scorer.scores["late"] += 1

        # save data to file
        datalog.flush()

    # Brief blank period to rest eyes and signal block change
    screen.show_cue(f"{block} / {totBlocks}", )
    logging.info('Starting block switch rest period')
    core.wait(CONF["fixation"]["restTime"])

###########
# Concluion

# End main experiment
screen.show_cue("DONE!")
core.wait(CONF["timing"]["cue"])

# Get data score


# Blank screen for final rest
screen.show_blank()
logging.info('Starting blank period')
# TODO: send start trigger
core.wait(CONF["timing"]["rest"])
# TODO: send end wait trigger

logging.info('Finished')


quitExperimentIf(True)
