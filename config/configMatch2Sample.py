import os
from config.configSession import CONF


CONF.update({
    "task": {
        "name": "match2sample",
        "duration": 2*80,  # 2 * 60,  # duration of a block, in seconds
        "blocks": 3,  # number of blocks, try to be even
        "trials": 10,  # number of trials per condition
        "levels": [1, 3, 6],
        "stimTime": 2,  # in seconds, min time to be considered a valid RT
        # time window after stimulus disappearance when it still counts as a key response
        "retentionTime":  1,  # 6,
        "probeTime": 2,
        "maxMissed": 3,


    },
    "stimuli": {
        "location": os.path.join("stimuli", "jediAlphabet"),
        # needs to be large enough for max number of stimuli
        "gridDimentions": [2, 3],  # number of cells in rows and columns
        "cellHeight": 3,  # in cm
        "stimHeight": 1,

    },
    "pause": {
        "backgroundColor": "black",
        "duration": 1  # figure it out
    },
    "instructions": {
        "text": "You will be presented with either 1, 3, or 6 stimuli. After a delay, a symbol will be shown, and you must indicate with 1 if it was included, or 0 if it was not in the original set.",
        "startPrompt": "Press any key to start. Press q to quit."
    },
    "tones": {
        "alarm": "horn.wav",
    }
})


CONF["screen"]["size"] = CONF["screen"]["size"] if CONF["screen"]["full"] else CONF["screen"]["debugSize"]
CONF["screen"]["resolution"] = CONF["screen"]["resolution"] if CONF["screen"]["full"] else CONF["screen"]["debugResolution"]
