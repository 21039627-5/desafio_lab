import sqlite3
import os
from config.settings import PROCESSED_FOLDER


DATABASE_PATH = os.path.join(PROCESSED_FOLDER, 'orders.db')

def init_db():
    """Inicializa o banco de dados e cria as tabelas necessárias."""
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            total REAL,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            value REAL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    """Retorna uma conexão com o banco de dados."""
    return sqlite3.connect(DATABASE_PATH)