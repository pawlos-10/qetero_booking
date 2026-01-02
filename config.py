"""
Configuration file for Qetero Booking System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Secret key for session management
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-qetero-booking-2025'

# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/qetero_booking.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Admin credentials (can be changed via admin panel later)
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@qetero.com'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'

