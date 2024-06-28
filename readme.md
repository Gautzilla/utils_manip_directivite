# Utils for the listening test on source directivity

This repo contains utilities that helped develop the [listening test application on the perception of sound source directivity](https://github.com/Gautzilla/manip_directivite).

## Content

|File|Description|
|:---|---:|
|`manip-dir-data/generate_lists.py`|Generates the `Phrases.csv` file, which contains pseudorandom sentences that match each required combination of the parameters of the listening test.|
|`manip-dir-data/sentence_generator.py`|Generate pseudorandom sentences based on either one of two head movement types: small head movements (e.g. *Yes, I have seen Fargo, but no, I have never seen Duel.*) and large head movements (e.g. *In this room, there is a carpet on the floor, a window on the left, a bed on the right and a light on the ceiling.*).|
|`manip-dir-data/independant_variables.py`|Generates all the combinations of the states of the independant variables for the listening test.|
|`movement_analysis.py`|Plots the head movements written during the recording of the sentences, and computes the mean error between the movements of the human speaker and the reproduction of the movements by the loudspeaker.|
|`reaper_session_marker_naming`|Rename the markers of the Reaper recording session, so that the audio files can be exported with a filename that explicit the state of the independant variable according to which they were recorded.|
|`spectruminvert.py`|EQ matching between sounds emitted by the human speaker and by the loudspeaker that allow the timbre of the two sources to be similar in their facing direction.|