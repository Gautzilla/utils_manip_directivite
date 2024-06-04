from sentence_generator import gen_sentence_small, gen_sentence_large
from independant_variables import get_recording_combinations, Amplitude, Room, Source
import pandas as pd
from random import random
from itertools import product

NB_RECORDING_REPETITIONS = 3 # Each sentence is recorded three times in the anechoic booth. In each room, different recordings will be played, and a spare one is recorded as a backup

def add_sentences(data):    
     for i in range(len(data)):
          data[i]["Sentence"] = gen_sentence_small() if data[i]["Amplitude"] == Amplitude.Small.name else gen_sentence_large()
     return data

def duplicate_lines(data):
     # RECORDING - Sentences to be printed for the anechoic recordings
     for i in range(len(data)):
         line_static = data[i]
         line_static["Rec_Repe"] = 0
         line_dynamic = line_static.copy()
         line_dynamic["Movement"] = True
         line_dynamic["Random"] = random()
         data.append(line_dynamic)
         line_static["Movement"] = False
         line_dynamic["Random"] = random()
         for i in range(NB_RECORDING_REPETITIONS-1):
               temp_static = line_static.copy()
               temp_dynamic = line_dynamic.copy()
               temp_static["Random"] = random()
               temp_dynamic["Random"] = random()
               temp_static["Rec_Repe"] = i+1
               temp_dynamic["Rec_Repe"] = i+1
               data.append(temp_static)
               data.append(temp_dynamic)
     return data

def create_test_dataframe(recording_dataframe):
     filtered_df = recording_dataframe.loc[(recording_dataframe.Rec_Repe == 0)]
     filtered_df = filtered_df.reset_index(drop = True)
     additional_levels = [(room.name, source.name) for room, source in product(Room, Source)]
     test_df = pd.DataFrame(columns = filtered_df.columns)
     for row in range(len(filtered_df)):
          for index, (room, source) in enumerate(additional_levels):
               i = row*len(additional_levels)+index
               test_df.loc[i]=filtered_df.loc[row]
               test_df.at[i,'Room'] = room
               test_df.at[i,'Source'] = source
     return test_df

def write_sentences(df):
     df = df.sort_values(by = ['Distance', 'Base Angle', 'Rec_Repe', 'Random'])
     df = df.reset_index(drop = True)
     df = df[['Distance', 'Base Angle', 'Movement', 'Repetition', 'Rec_Repe', 'Sentence']]
     df.to_csv(r'C:\Users\User\Desktop\Phrases.csv', index = True)

def write_test_df(df):
     df = df.sort_values(by = ['Room', 'Distance', 'Base Angle', 'Amplitude', 'Movement', 'Source'])
     df = df.reset_index(drop = True)
     df = df[['Room', 'Distance', 'Base Angle', 'Amplitude', 'Movement', 'Source', 'Sentence']]
     df.to_csv(r'C:\Users\User\Desktop\Stimuli.csv', index = True)

def create_recording_dataframe(number_of_repetitions = 3):
    data = get_recording_combinations(number_of_repetitions)
    data = add_sentences(data)
    data = duplicate_lines(data)
    return pd.DataFrame(data)

def main():
    recording_df = create_recording_dataframe(number_of_repetitions = 3)
    write_sentences(recording_df)
    test_df = create_test_dataframe(recording_df)
    write_test_df(test_df)
    return

if (__name__ == '__main__'):  
    main()