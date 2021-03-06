import logging
import os
import random
import time
import datetime
import sys
import math


from screen import Screen
from scorer import Scorer
from trigger import Trigger
from psychopy import core, event, sound
from psychopy.hardware import keyboard
from pupil_labs import PupilCore
from datalog import Datalog

from config.configMatch2Sample import CONF

#########################################################################

# Initialize screen, logger and inputs
logging.basicConfig(
    level=CONF["loggingLevel"],
    format='%(asctime)s-%(levelname)s-%(message)s',
)  # This is a log for debugging the script, and prints messages to the terminal


# needs to be first, so that if it doesn't succeed, it doesn't freeze everything
eyetracker = PupilCore(ip=CONF["pupillometry"]
                       ["ip"], port=CONF["pupillometry"]["port"], shouldRecord=CONF["recordEyetracking"])

trigger = Trigger(CONF["trigger"]["serial_device"],
                  CONF["sendTriggers"], CONF["trigger"]["labels"])

screen = Screen(CONF)

scorer = Scorer()


datalog = Datalog(OUTPUT_FOLDER=os.path.join(
    'output', CONF["participant"] + "_" + CONF["session"]), CONF=CONF)  # This is for saving data TODO: apply everywhere

kb = keyboard.Keyboard()

mainClock = core.MonotonicClock()  # starts clock for timestamping events

alarm = sound.Sound(os.path.join('sounds', CONF["instructions"]["alarm"]),
                    stereo=True)

questionnaireReminder = sound.Sound(os.path.join(
    'sounds', CONF["instructions"]["questionnaireReminder"]), stereo=True)

logging.info('Initialization completed')

#########################################################################


def quitExperimentIf(shouldQuit):
    "Quit experiment if condition is met"

    if shouldQuit:
        trigger.send("Quit")
        scorer.getScore()
        logging.info('quit experiment')
        trigger.reset()
        eyetracker.stop_recording()
        sys.exit(2)


def onFlip(stimName, logName):
    trigger.send(stimName)
    kb.clock.reset()  # this starts the keyboard clock as soon as stimulus appears
    datalog[logName] = mainClock.getTime()

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


eyetracker.start_recording(os.path.join(
    CONF["participant"], CONF["task"]["name"], CONF["session"]))

# Blank screen for initial rest
screen.show_blank()
logging.info('Starting blank period')

trigger.send("StartBlank")
core.wait(CONF["timing"]["rest"])
trigger.send("EndBlank")

# Cue start of the experiment
screen.show_cue("START")
trigger.send("Start")
core.wait(CONF["timing"]["cue"])

##########################################################################


#################
# Main experiment
#################

# initialize variables
totBlocks = CONF["task"]["blocks"]

conditions = [(levels, matches) for levels in CONF["task"]["levels"]
              for matches in [True, False]] * math.ceil(CONF["task"]["trials"]/2)


# loop through blocks and trials
for block in range(1, totBlocks + 1):

    # set counter
    totMissed = 0

    # set block conditions
    random.shuffle(conditions)

    logging.info(f"{block} / {totBlocks}")

    # start block
    for trial, condition in enumerate(conditions):
        logging.info('Starting trial #%s with %s stimuli',
                     trial + 1, condition[0])

        triggerId = trigger.sendTriggerId()
        datalog["triggerID"] = triggerId

        ###############
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
                quitExperimentIf(key[0].name == 'q')
                extraKeys.append(mainClock.getTime())
                trigger.send("BadResponse")

            core.wait(0.1)

        #######################
        # Stimulus presentation

        # show fixation first
        screen.show_fixation()
        core.wait(CONF["timing"]["cue"])

        # show stimulus
        eyetracker.send_trigger(
            "Stim", {"block": block, "trial": trial, "level": condition})
        screen.window.callOnFlip(onFlip, "Stim", "startTime")
        screen.show_new_grid(condition[0])
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
        if condition[1]:
            # TODO one day: make this not random, but counterbalanced
            probe = random.choice(screen.stimuli["filenames"])
            probeTrigger = "MatchProbe"
        else:
            notShown = set(screen.files) - set(screen.stimuli)
            probe = random.choice(list(notShown))
            probeTrigger = "NonMatchProbe"

        # show probe stimulus
        eyetracker.send_trigger(
            "Probe", {"block": block, "trial": trial, "matches": probeTrigger})

        screen.window.callOnFlip(onFlip, probeTrigger, "probeTime")
        screen.show_probe(probe)
        responseTimer = core.CountdownTimer(CONF["task"]["probeTime"])

        Missed = True
        while responseTimer.getTime() > 0:
            key = kb.getKeys()
            if key:
                answer = key[0].name
                quitExperimentIf(answer == 'q')

                if answer not in CONF["task"]["answerKeys"]:
                    responseTrigger = "BadResponse"
                elif condition[1] and answer == CONF["task"]["answerKeys"][0]:
                    responseTrigger = "CorrectAnswer"
                elif not condition[1] and answer == CONF["task"]["answerKeys"][1]:
                    responseTrigger = "CorrectAnswer"
                else:
                    responseTrigger = "IncorrectAnswer"

                trigger.send(responseTrigger)
                eyetracker.send_trigger(
                    "Response", {"answer": responseTrigger})
                datalog["responseTrigger"] = responseTrigger
                Missed = False
                break

        # log data
        datalog["level"] = condition[0]
        datalog["block"] = block
        datalog["trial"] = trial

        datalog["stimuli"] = screen.stimuli
        datalog["probe"] = probe
        datalog["shouldMatch"] = condition[1]

        if Missed:
            datalog["missed"] = True
            scorer.newAnswer("missed")
            totMissed += 1
            if totMissed > CONF["task"]["maxMissed"]:
                trigger.send("ALARM")
                alarm.play()
                datalog["alarm"] = mainClock.getTime()
                logging.warning("alarm sound!!!!!")
        else:
            datalog["response"] = key[0].name
            datalog["RT"] = key[0].rt
            scorer.newAnswer(responseTrigger)
            totMissed = 0

        logging.info("finished trial")

        # save data to file
        datalog.flush()

    # Brief blank period to rest eyes and signal block change
    screen.show_block_break(f"{block} / {totBlocks}")
    logging.info('Starting block switch rest period')
    key = event.waitKeys()
    quitExperimentIf(key[0] == 'q')

    core.wait(CONF["pause"]["duration"])

###########
# Concluion
###########

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
eyetracker.stop_recording()
questionnaireReminder.play()
core.wait(2)
