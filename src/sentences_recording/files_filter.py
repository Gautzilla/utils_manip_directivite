import sqlite3
import os

AUDIO_FOLDER = r'C:\Users\Gauthier\source\repos\manip_directivite\data\audio'
DB_PATH = r'C:\Users\Gauthier\source\repos\manip_directivite\data\manip_directivite.db'

def get_all_audio_files() -> list:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        query = 'SELECT recordings.audio_file FROM recordings'
        ratings = cursor.execute(query)
        return list([rating[0] for rating in ratings])

def main() -> None:
    audio_files_in_test = get_all_audio_files()
    for file in os.listdir(AUDIO_FOLDER):
        if file in audio_files_in_test:
            continue
        os.remove(os.path.join(AUDIO_FOLDER, file))

if __name__ == '__main__':
    main()