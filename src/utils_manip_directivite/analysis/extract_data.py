import sqlite3
from datetime import date
from random import gauss
import pandas as pd
from utils_manip_directivite import DB_PATH
from scipy.stats import zscore
from datetime import date
from statistics import mean, stdev

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
        ['Victoria', 'Legrand', date(1981, 5, 28)],
        ['Frank', 'Black', date(1965, 4, 6)],
        ['Cole', 'Alexander', date(1982, 6, 8)],
        ['Julian', 'Casablancas', date(1978, 8, 23)],
        ['James', 'Mercer', date(1970, 12, 26)],
        ['Ariel', 'Pink', date(1978, 6, 24)],
        ['Aphex', 'Twin', date(1971, 8, 18)]
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

def fill_db_with_random_data() -> None:    
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        delete_users(cursor)
        delete_ratings(cursor)
        add_dummy_users(cursor)
        add_dummy_ratings(cursor)

def gather_ratings(cursor: sqlite3.Cursor) -> list:
    query = """SELECT users.id, rooms.name, conditions.distance, conditions.angle, conditions.movement, conditions.source, sentences.amplitude, recordings.repetition, ratings.timbre, ratings.plausibility, ratings.angle, ratings.movement
    FROM ratings 
    INNER JOIN recordings ON ratings.recording_id = recordings.id
    INNER JOIN rooms ON recordings.room_id = rooms.id
    INNER JOIN users ON ratings.user_id = users.id
    INNER JOIN conditions ON recordings.conditions_id = conditions.id
    INNER JOIN sentences ON recordings.sentence_id = sentences.id
    WHERE users.id > 1"""
    ratings = cursor.execute(query)
    return ratings

def get_dataframe(z_score: bool) -> pd.DataFrame:
    ratings = []

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        ratings_cursor = gather_ratings(cursor)
        for rating in ratings_cursor:
            ratings.append(list(rating))

    df = pd.DataFrame(ratings, columns = ['user', 'room', 'distance', 'angle', 'movement', 'source', 'amplitude', 'repetition', 'answer_timbre', 'answer_plausibility', 'answer_angle', 'answer_movement'])

    if z_score:
        for rating in ['answer_plausibility', 'answer_timbre']:
            df[rating] = df.groupby('user')[rating].transform(lambda x: zscore(x, ddof = 1))

    return df

def get_birth_dates() -> list:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        query = "SELECT users.birth_date FROM users WHERE users.id > 1"
        birth_dates = [date(*[int(s) for s in c[0].split('-')]) for c in cursor.execute(query)]
    return birth_dates

def age(birth_date: date):
    test_date = date(year = 2024, month = 8, day = 1)
    return test_date.year - birth_date.year - ((test_date.month, test_date.day) < (birth_date.month, birth_date.day))

def get_ages() -> list:
    birth_dates = get_birth_dates()
    return [age(bd) for bd in birth_dates]

def age_summary() -> str:
    ages = get_ages()
    return f'Participants were {min(ages)} to {max(ages)} years old (µ = {mean(ages)}, σ ={stdev(ages)}).'

def main() -> None:
    df = get_dataframe(z_score=True)
    df.to_csv(r'C:\Users\User\Desktop\results_manip_dir.csv')


if __name__ == '__main__':
    main()
    
