import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file

class Config:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # SQLAlchemy connection string for MySQL via PyMySQL
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")

    UPLOAD_FOLDER = "static/uploads"
    CHROMA_DB_PATH = "chroma_db"