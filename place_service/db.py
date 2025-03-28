import sqlite3
from typing import Optional

DB_PATH = "places.db"

def create_table():
    """Создает таблицу, если её нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        address TEXT,
        category TEXT,
        rating REAL,
        latitude REAL,
        longitude REAL
    )
    ''')
    conn.commit()
    conn.close()

def save_place(name: str, address: str, category: str, rating: Optional[float], latitude: float, longitude: float):
    """Сохраняет место в базе данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO places (name, address, category, rating, latitude, longitude)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, address, category, rating, latitude, longitude))
    conn.commit()
    conn.close()
