import sqlite3
import os
from utils_manip_directivite import AUDIO_FOLDER, DB_PATH

def get_all_audio_files() -> list:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        query = 'SELECT recordings.audio_file FROM recordings'
        ratings = cursor.execute(query)
        return list([rating[0] for rating in ratings])
    
def remove_unused_files(audio_files_to_keep: list) -> int:
    count = 0
    for file in os.listdir(AUDIO_FOLDER):
        if file in audio_files_to_keep:
            continue
        os.remove(os.path.join(AUDIO_FOLDER, file))
        count += 1
    return count

def get_missing_files(audio_files_in_test: list) -> list:
    return [audio_file for audio_file in audio_files_in_test if audio_file not in os.listdir(AUDIO_FOLDER)]

def main() -> None:
    audio_files_in_test = get_all_audio_files()

    nb_removed_files = remove_unused_files(audio_files_to_keep = audio_files_in_test)
    print(f'Deleted files: {nb_removed_files}')

    missing_files = get_missing_files(audio_files_in_test = audio_files_in_test)
    print(f'Missing files: {len(missing_files)}')
    print(missing_files)

if __name__ == '__main__':
    main()