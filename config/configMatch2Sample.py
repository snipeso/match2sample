import os
from config.updateConfig import UpdateConfig


match2sampleCONF = {
    "task": {
        "name": "match2sample",
        "blocks": {"versionMain": 4, "versionDemo": 1, "versionDebug": 1},
        # number of trials per condition
        "trials":  {"versionMain": 10, "versionDemo": 30, "versionDebug": 5},
        "levels":  {"versionMain": [1, 3, 6], "versionDemo": [1], "versionDebug": [1, 3, 6]},
        "stimTime": 2,  # in seconds, min time to be considered a valid RT
        # time window after stimulus disappearance when it still counts as a key response
        "retentionTime": {"versionMain": 4, "versionDemo": 1, "versionDebug": 1},
        "probeTime": 3,
        "answerKeys": ["right", "left", ],  # mismatch and match respectively
        "maxMissed": 3
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
        "duration": 2
    },
    "instructions": {
        "text": "You will be presented with either 1, 3, or 6 symbols at once. After a delay, a 'probe' symbol will be shown, and you must indicate with the LEFT arrow if it was included in the previous set, or with the RIGHT arrow if it was not. You hae 3 seconds to respond.",
        "startPrompt": "Press any key to continue. Press q to quit.",
        "matchImage": os.path.join("stimuli", "probe", "check.JPG"),
        "mismatchImage": os.path.join("stimuli", "probe", "x.JPG"),
        "matchPos": (5, 0),  # in cm
        "mismatchPos": (-5, 0),
        "matchSize": (1, 1),
        "alarm": "horn.wav",
    }
}


match2sampleTriggers = {
    "StartFix": 10,
    "MatchProbe": 11,
    "NonMatchProbe": 12,
    "CorrectAnswer": 13,
    "IncorrectAnswer": 14
}


updateCofig = UpdateConfig()
updateCofig.addContent(match2sampleCONF)
updateCofig.addTriggers(match2sampleTriggers)

CONF = updateCofig.getConfig()
