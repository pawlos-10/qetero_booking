"""
Database connection and utilities using sqlite3
"""
import sqlite3
import os
from datetime import datetime
from functools import wraps
from pathlib import Path

# Database file path
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'qetero_booking.db'


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            role TEXT NOT NULL DEFAULT 'patient',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index on email
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    
    # Doctors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            specialty TEXT NOT NULL,
            bio TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Schedules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            is_available INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
        )
    ''')
    
    # Appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date DATE NOT NULL,
            appointment_time TIME NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()


def dict_factory(cursor, row):
    """Convert row to dictionary"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

