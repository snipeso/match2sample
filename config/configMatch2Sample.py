import os
from config.configSession import CONF


CONF.update({
    "task": {
        "name": "match2sample",
        "duration": 2*80,  # 2 * 60,  # duration of a block, in seconds
        "blocks": 3,  # number of blocks, try to be even
        "trials": 10,  # number of trials per condition
        "levels": [1, 3, 6],
        "stimTime": 3,  # in seconds, min time to be considered a valid RT
        # time window after stimulus disappearance when it still counts as a key response
        "retentionTime":  1,  # 7,
        "probeTime": 3,
        "maxMissed": 3,
        "answerKeys": ["left", "right"]  # match and mismatch respectively

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
        "duration": 1  # figure it out
    },
    "instructions": {
        "text": "You will be presented with either 1, 3, or 6 stimuli. After a delay, a symbol will be shown, and you must indicate with LEFT arrow if it was included, or RIGHT arrow if it was not in the original set.",
        "startPrompt": "Press any key to start. Press q to quit.",
        "matchImage": os.path.join("stimuli", "probe", "check.png"),
        "mismatchImage": os.path.join("stimuli", "probe", "x.png"),
        "matchPos": (-5, 0),  # in cm
        "mismatchPos": (5, 0),
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
