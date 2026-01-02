import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-qetero-booking-2025'

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/qetero_booking.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
    
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@qetero.com'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'

