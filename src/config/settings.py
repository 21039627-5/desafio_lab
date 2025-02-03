import os

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
PROCESSED_FOLDER = os.getenv('PROCESSED_FOLDER', './processed')
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///orders.db')

