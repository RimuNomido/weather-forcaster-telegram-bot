import sqlite3
import json

db_name = 'queries.db'

def init_db():
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS queries (
        user_id INTEGER,
        city TEXT NOT NULL,
        weather_data JSON
        )
    ''')

    connection.commit()

    return connection, cursor

connection, cursor = init_db()

def save_query(user_id, city, weather_data):
    data = json.dumps(weather_data, ensure_ascii=False)
    cursor.execute('INSERT INTO queries (user_id, city, weather_data) VALUES (?, ?, ?)', (user_id, city, data))
    connection.commit()

def get_queries(user_id):
    cursor.execute('SELECT city, weather_data FROM queries WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    return rows[-10::]

def get_queries_count(user_id):
    cursor.execute('SELECT COUNT(*) FROM queries WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    return len(rows)

def clear_queries(user_id):
    cursor.execute('DELETE FROM queries WHERE user_id = ?', (user_id,))
    connection.commit()