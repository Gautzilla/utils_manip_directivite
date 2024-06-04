import pandas as pd
import numpy as np

TAKE_LENGTH = 60
TAKE_OFFSET = 60

def get_reaper_session(reaper_session_name: str) -> str:
    reaper_session = open(reaper_session_name, 'r')
    text = reaper_session.read()
    reaper_session.close()    
    return text

def write_markers_names(phrases: np.array, reaper_session: str) -> str:
    for phrase in phrases:
        marker_id, distance, angle, movement, repetition, rec_repetition = phrase[:-1]
        marker_name_parameters = list(map(lambda x: str(x), [distance, angle, movement, repetition, rec_repetition]))
        marker_name = '_'.join(marker_name_parameters)
        old_marker_id = f'MARKER {marker_id} {marker_id*TAKE_LENGTH + TAKE_OFFSET} ""'
        new_marker_id = f'MARKER {marker_id} {marker_id*TAKE_LENGTH + TAKE_OFFSET} "{marker_name}"'
        print(f'Replacing {old_marker_id} with {new_marker_id}')
        reaper_session = reaper_session.replace(old_marker_id, new_marker_id)
    return reaper_session

def write_new_session(reaper_session_name: str, reaper_session: str):
    f = open(reaper_session_name + '_with_marker_names.rpp', 'w')
    f.write(reaper_session)
    f.close()

def main():
    reaper_session_name = 'EnregistrementAnechoique_temp'
    reaper_session = get_reaper_session(reaper_session_name + '.rpp')
    phrases = pd.read_csv('Phrases.csv').to_numpy()
    new_session = write_markers_names(phrases, reaper_session)
    write_new_session(reaper_session_name, new_session)
    
if __name__ == '__main__':
    main()