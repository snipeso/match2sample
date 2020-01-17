import logging
import os
import random
import time
import datetime
import sys
# import psychtoolbox as ptb

from chronometer import Chronometer
from screen import Screen
from scorer import Scorer
from psychopy import core, event, sound
from psychopy.hardware import keyboard

from datalog import Datalog
from config.configMatch2Sample import CONF

#########################################################################

# Initialize screen, logger and inputs
logging.basicConfig(
    level=CONF["loggingLevel"],
    format='%(asctime)s-%(levelname)s-%(message)s',
)  # This is a log for debugging the script, and prints messages to the terminal

screen = Screen(CONF)
scorer = Scorer()
datalog = Datalog(OUTPUT_FOLDER=os.path.join(
    'output', datetime.datetime.now(
    ).strftime("%Y-%m-%d")), CONF=CONF)  # This is for saving data
kb = keyboard.Keyboard()
mainClock = core.MonotonicClock()  # starts clock for timestamping events
alarm = sound.Sound(os.path.join('sounds', CONF["tones"]["alarm"]),
                    stereo=True)

# Experiment conditions
# showLeft = random.choice([True, False])


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


# # Display overview of session
# screen.show_overview()
# core.wait(CONF["timing"]["overview"])

# # Optionally, display instructions
# if CONF["showInstructions"]:
#     screen.show_instructions()
#     key = event.waitKeys()
#     quitExperimentIf(key[0] == 'q')

# # Blank screen for initial rest
# screen.show_blank()
# logging.info('Starting blank period')

# # TODO: send start trigger
# core.wait(CONF["timing"]["rest"])
# # TODO: send end wait trigger

# # Cue start of the experiment
# screen.show_cue("START")
# core.wait(CONF["timing"]["cue"])

##########################################################################

#################
# Main experiment
#################

# initialize variables
stimulus_number = 0
totBlocks = CONF["task"]["blocks"]
levels = CONF["task"]["levels"] * CONF["task"]["trials"]
# shouldMatch = [True] * len(levels)/2 + [False] * \
#     len(levels)/2  # probe matches half the time
shouldMatch = [True] * 3 + [False]

################################################
# loop through blocks and trials
for block in range(1, totBlocks + 1):

    # set counter
    totMissed = 0

    # set block conditions
    random.shuffle(levels)
    random.shuffle(shouldMatch)
    print(levels)

    logging.info(f"{block} / {totBlocks}")

    # start block
    for trial in range(len(levels)):
        level = levels[trial]
        logging.info('Starting trial #%s with %s stimuli',
                     trial + 1, level)

        ###############################
        # Wait a little

        screen.show_blank()

        # start delay
        delayTimer = core.CountdownTimer(CONF["pause"]["duration"])
        logging.info("starting delay of %s", delayTimer)

        extraKeys = []
        while delayTimer.getTime() > 0:
            #  Record any extra key presses during wait
            key = kb.getKeys()
            if key:
                # TODO: make seperate function that also keeps track of q, make q in config
                quitExperimentIf(key[0].name == 'q')
                extraKeys.append(mainClock.getTime())

            core.wait(0.1)

        #######################
        # Stimulus presentation
        stimuli = screen.show_new_grid(level)
        core.wait(CONF["task"]["stimTime"])

        screen.show_blank()
        core.wait(CONF["task"]["retentionTime"])

        if shouldMatch[trial]:
            # TODO one day: make this not random, but counterbalanced
            probe = random.choice(stimuli["filenames"])

        screen.show_probe(probe)
        responseTimer = core.CountdownTimer(CONF["task"]["probeTime"])

        Missed = True
        while responseTimer.getTime() > 0:
            key = kb.getKeys()
            if key:
                quitExperimentIf(key[0].name == 'q')
                Missed = False
                break

        # log data
        # TODO, save stimuli
        datalog["level"] = level
        datalog["block"] = block
        datalog["trial"] = trial
        datalog["extrakeypresses"] = extraKeys
        datalog["stimuli"] = stimuli
        datalog["probe"] = probe
        datalog["shouldMatch"] = shouldMatch[trial]
        logging.info("finished trial")

        # save data to file
        datalog.flush()

    # Brief blank period to rest eyes and signal block change
    screen.show_cue(f"{block} / {totBlocks}", )
    logging.info('Starting block switch rest period')
    core.wait(CONF["pause"]["duration"])

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
