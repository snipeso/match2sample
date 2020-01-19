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
from trigger import Trigger
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
trigger = Trigger(CONF["trigger"]["serial_device"],
                  CONF["sendTriggers"], CONF["trigger"]["labels"])
datalog = Datalog(OUTPUT_FOLDER=os.path.join(
    'output', datetime.datetime.now(
    ).strftime("%Y-%m-%d")), CONF=CONF)  # This is for saving data
kb = keyboard.Keyboard()
mainClock = core.MonotonicClock()  # starts clock for timestamping events
alarm = sound.Sound(os.path.join('sounds', CONF["tones"]["alarm"]),
                    stereo=True)


logging.info('Initialization completed')

#########################################################################


def quitExperimentIf(shouldQuit):
    "Quit experiment if condition is met"

    if shouldQuit:
        trigger.send("Quit")
        scorer.getScore()
        logging.info('quit experiment')
        sys.exit(2)  # TODO: make version where quit is sys 1 vs sys 2


def onFlip():
    trigger.send("Stim")
    kb.clock.reset()  # this starts the keyboard clock as soon as stimulus appears
    datalog["startTime"] = mainClock.getTime()

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

# trigger.send("StartBlank")
# core.wait(CONF["timing"]["rest"])
# trigger.send("EndBlank")

# # Cue start of the experiment
# screen.show_cue("START")
# trigger.send("Start")
# core.wait(CONF["timing"]["cue"])

##########################################################################

#################
# Main experiment
#################

# initialize variables
stimulus_number = 0
totBlocks = CONF["task"]["blocks"]
levels = CONF["task"]["levels"] * CONF["task"]["trials"]
shouldMatch = [True] * int(len(levels)/2) + [False] * \
    int(len(levels)/2)  # probe matches half the time


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
                trigger.send("BadResponse")

            core.wait(0.1)

        #######################
        # Stimulus presentation

        # show stimulus
        screen.window.callOnFlip(onFlip)
        screen.show_new_grid(level)
        core.wait(CONF["task"]["stimTime"])

        # show just fixation dot
        screen.show_fixation()
        trigger.send("StartFix")
        retentionTimer = core.CountdownTimer(CONF["task"]["retentionTime"])

        while retentionTimer.getTime() > 0:
            #  Record any extra key presses during wait
            key = kb.getKeys()
            if key:
                quitExperimentIf(key[0].name == 'q')
                extraKeys.append(mainClock.getTime())
                trigger.send("BadResponse")

            core.wait(0.01)

        # log all extra key presses
        scorer.scores["extraKeys"] += len(extraKeys)
        datalog["extrakeypresses"] = extraKeys

        # determine probe stimulus
        if shouldMatch[trial]:
            # TODO one day: make this not random, but counterbalanced
            probe = random.choice(screen.stimuli["filenames"])
        else:
            notShown = set(screen.files) - set(screen.stimuli)
            probe = random.choice(list(notShown))

        # show probe stimulus
        screen.show_probe(probe)
        trigger.send("Probe")  # TODO, make this happen on flip! so fast!
        responseTimer = core.CountdownTimer(CONF["task"]["probeTime"])

        Missed = True
        while responseTimer.getTime() > 0:
            key = kb.getKeys()
            if key:
                quitExperimentIf(key[0].name == 'q')
                trigger.send("Response")
                Missed = False
                break

        # log data
        datalog["level"] = level
        datalog["block"] = block
        datalog["trial"] = trial

        datalog["stimuli"] = screen.stimuli
        datalog["probe"] = probe
        datalog["shouldMatch"] = shouldMatch[trial]

        if Missed:
            datalog["missed"] = True
        else:
            datalog["response"] = key[0].name
            datalog["RT"] = key[0].rt

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
trigger.send("End")
core.wait(CONF["timing"]["cue"])

# Blank screen for final rest
screen.show_blank()
logging.info('Starting blank period')

trigger.send("StartBlank")
core.wait(CONF["timing"]["rest"])
trigger.send("EndBlank")


logging.info('Finished')
scorer.getScore()
trigger.reset()
