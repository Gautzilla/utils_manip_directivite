import sqlite3
from datetime import date
from random import gauss
import pandas as pd

DB_PATH = r'C:\Users\Gauthier\source\repos\manip_directivite\data\manip_directivite.db'

def delete_users(cursor: sqlite3.Cursor) -> None:
    cursor.execute('DELETE FROM users')

def delete_ratings(cursor: sqlite3.Cursor) -> None:
    cursor.execute('DELETE FROM ratings')

def add_dummy_users(cursor: sqlite3.Cursor) -> None:
    users = [
        ['Gauthier', 'Berthomieu', date(1994, 6, 16)],
        ['Justine', 'Provost', date(1990, 5, 9)],
        ['Mac', 'DeMarco', date(1990, 5, 30)],
        ['Connan', 'Mockasin', date(1983, 3, 21)],
        ['Victoria', 'Legrand', date(1981, 5, 28)]
        ]

    for user in users:
        cursor.execute(f'INSERT INTO users (first_name,last_name,birth_date) VALUES ("{user[0]}", "{user[1]}", "{user[2]}")')

def set_random_ratings(recording: tuple) -> tuple:
    is_dynamic = recording[1] == 0
    is_human = recording[2] == 'Human'
    timbre = gauss(.5, .5)
    width = gauss(.7 if is_human else .4, .3)
    plausibility_mean = .6 if is_human else .4
    plausibility_mean = plausibility_mean + (0.2 if is_dynamic else -0.2)
    plausibily_sigma = .1 if is_human else .4
    plausibility = gauss(plausibility_mean, plausibily_sigma)
    
    (t,w,p) = (min(1.,max(0.,v)) for v in (timbre, width, plausibility))
    return (t,w,p)

def add_dummy_ratings(cursor: sqlite3.Cursor) -> None:
    recordings  = cursor.execute('SELECT recordings.id, conditions.movement, conditions.source FROM recordings INNER JOIN conditions ON recordings.conditions_id = conditions.id').fetchall()
    user_ids = [i[0] for i in cursor.execute('SELECT id FROM users').fetchall()]
    for user_id in user_ids:
        for recording in recordings:
            recording_id = recording[0]
            timbre, width, plausibility = set_random_ratings(recording)
            cursor.execute(f'INSERT INTO ratings (user_id, recording_id, timbre, plausibility, source_width) VALUES ({user_id}, {recording_id}, {timbre}, {plausibility}, {width})')

def fill_db_with_random_data(cursor: sqlite3.Cursor) -> None:
    delete_users(cursor)
    delete_ratings(cursor)
    add_dummy_users(cursor)
    add_dummy_ratings(cursor)

def gather_ratings(cursor: sqlite3.Cursor) -> list:
    query = """SELECT users.id, rooms.name, conditions.distance, conditions.angle, conditions.movement, conditions.source, sentences.amplitude, ratings.timbre, ratings.source_width, ratings.plausibility
    FROM ratings 
    INNER JOIN recordings ON ratings.recording_id = recordings.id
    INNER JOIN rooms ON recordings.room_id = rooms.id
    INNER JOIN users ON ratings.user_id = users.id
    INNER JOIN conditions ON recordings.conditions_id = conditions.id
    INNER JOIN sentences ON recordings.sentence_id = sentences.id"""
    ratings = cursor.execute(query)
    return ratings

def main() -> None:
    ratings = []

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        #fill_db_with_random_data(cursor)
        ratings_cursor = gather_ratings(cursor)
        
        for rating in ratings_cursor:
            ratings.append(list(rating))

    df = pd.DataFrame(ratings, columns = ['user', 'room', 'distance', 'angle', 'movement', 'source', 'amplitude', 'timbre', 'source_width', 'plausibility'])
    df.to_csv(r'C:\Users\Gauthier\Desktop\results_manip_dir.csv')


if __name__ == '__main__':
    main()
    
