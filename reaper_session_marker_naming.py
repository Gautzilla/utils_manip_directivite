import pandas as pd
import numpy as np
import os

TAKE_LENGTH = 60
TAKE_OFFSET = 60

def get_reaper_session(reaper_session_name: str) -> str:
    reaper_session = open(reaper_session_name, 'r')
    text = reaper_session.read()
    reaper_session.close()    
    return text    

def write_markers_names(sentences: pd.DataFrame, reaper_session: str) -> str:
    for i in range(len(sentences['ID'])):
        sentence = sentences.iloc[i]
        id = sentence.loc['ID']
        distance = sentence.loc['D']
        angle = sentence.loc['A']
        movement = sentence.loc['M']
        repetition = sentence.loc['N']
        rec_repetition = sentence.loc['Rec_N']
        marker_name_parameters = list(map(lambda x: str(x), [distance, angle, movement, repetition, rec_repetition]))
        marker_name = '_'.join(marker_name_parameters)
        old_marker_id = f'MARKER {id} {id*TAKE_LENGTH + TAKE_OFFSET} ""'
        new_marker_id = f'MARKER {id} {id*TAKE_LENGTH + TAKE_OFFSET} "{marker_name}"'
        print(f'Replacing {old_marker_id} with {new_marker_id}')
        reaper_session = reaper_session.replace(old_marker_id, new_marker_id)
    return reaper_session

def write_new_session(reaper_session_name: str, reaper_session: str):
    f = open(reaper_session_name + '_with_marker_names.rpp', 'w')
    f.write(reaper_session)
    f.close()

def main():
    folder = r'C:\Users\labsticc\Desktop\temp'
    reaper_session_name = os.path.join(folder, 'EnregistrementAnechoique')
    reaper_session = get_reaper_session(reaper_session_name + '.rpp')
    phrases = pd.read_csv(os.path.join(folder, 'Phrases.csv'))
    new_session = write_markers_names(phrases, reaper_session)
    write_new_session(reaper_session_name, new_session)
    
if __name__ == '__main__':
    main()