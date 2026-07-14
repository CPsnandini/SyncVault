import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

_db_url = os.getenv("DATABASE_URL", "sqlite:///syncvault.db")
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STORAGE_DIR = os.path.join(BASE_DIR, "storage")
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024