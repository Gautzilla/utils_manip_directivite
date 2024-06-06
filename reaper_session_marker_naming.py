import pandas as pd
import numpy as np
import os
import re

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
        reaper_session = reaper_session.replace(old_marker_id, new_marker_id)
    return reaper_session

def add_repetition_ordering(sentences:pd.DataFrame, reaper_session: str) -> str:
    if 'M_r' not in sentences.columns:
        return reaper_session
    
    for i in range(len(sentences['ID'])):
        sentence = sentences.iloc[i]
        id = sentence.loc['ID']
        rec_repetition_rating = sentence.loc['M_r']
        pattern = rf'MARKER {id} \d+ "\w+_\w+_\w+_\d+_\d+_\w+"'
        old_marker_name = re.search(pattern, reaper_session).group()
        new_marker_name = f'{old_marker_name.strip('"')}_{rec_repetition_rating}"'
        print(f'Replacing {old_marker_name} with {new_marker_name}')
        reaper_session = reaper_session.replace(old_marker_name, new_marker_name)
    return reaper_session


def write_new_session(reaper_session_name: str, reaper_session: str):
    f = open(reaper_session_name, 'w')
    f.write(reaper_session)
    f.close()

def main():
    folder = r'C:\Users\labsticc\Desktop\temp'
    reaper_session_name = os.path.join(folder, 'EnregistrementAnechoique')
    reaper_session = get_reaper_session(reaper_session_name + '.rpp')
    phrases = pd.read_csv(os.path.join(folder, 'Phrases.csv'))
    new_session = write_markers_names(phrases, reaper_session)
    write_new_session(reaper_session_name + '_with_marker_names.rpp', new_session)
    new_session_ratings = add_repetition_ordering(phrases, new_session)
    write_new_session(reaper_session_name + '_with_ratings.rpp', new_session_ratings)
    
if __name__ == '__main__':
    main()