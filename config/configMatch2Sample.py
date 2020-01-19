import os
from config.configSession import CONF


CONF.update({
    "task": {
        "name": "match2sample",
        "blocks": 4,  # number of blocks, try to be even
        "trials": 10,  # number of trials per condition
        "levels": [1, 3, 6],
        "stimTime": 2,  # in seconds, min time to be considered a valid RT
        # time window after stimulus disappearance when it still counts as a key response
        "retentionTime": 4,
        "probeTime": 3,
        "answerKeys": ["right", "left", ]  # mismatch and match respectively

    },
    "stimuli": {
        "location": os.path.join("stimuli", "jediAlphabet"),
        # needs to be large enough for max number of stimuli
        "gridDimentions": [3, 3],  # number of cells in rows and columns
        "cellHeight": 2,  # in cm
        "stimSize": (2, 2),

    },
    "pause": {
        "backgroundColor": "black",
        "duration": 2  # figure it out
    },
    "instructions": {
        "text": "You will be presented with either 1, 3, or 6 symbols at once. After a delay, a 'probe' symbol will be shown, and you must indicate with the LEFT arrow if it was included in the previous set, or with the RIGHT arrow if it was not. You hae 3 seconds to respond.",
        "startPrompt": "Press any key to continue. Press q to quit.",
        "matchImage": os.path.join("stimuli", "probe", "check.png"),
        "mismatchImage": os.path.join("stimuli", "probe", "x.png"),
        "matchPos": (5, 0),  # in cm
        "mismatchPos": (-5, 0),
        "matchSize": (1, 1)
    },
    "tones": {
        "alarm": "horn.wav",
    }
})


CONF["screen"]["size"] = CONF["screen"]["size"] if CONF["screen"]["full"] else CONF["screen"]["debugSize"]
CONF["screen"]["resolution"] = CONF["screen"]["resolution"] if CONF["screen"]["full"] else CONF["screen"]["debugResolution"]

# additional triggers
CONF["trigger"]["labels"]["StartFix"] = 0x0A
CONF["trigger"]["labels"]["MatchProbe"] = 0x0B
CONF["trigger"]["labels"]["NonMatchProbe"] = 0x0C
CONF["trigger"]["labels"]["CorrectAnswer"] = 0x0D
CONF["trigger"]["labels"]["IncorrectAnswer"] = 0x0E
