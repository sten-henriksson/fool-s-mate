from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, Response
import logging
import sqlite3
import os

# Database configuration
DATABASE_PATH = "api_keys2.db"

# Initialize database if it doesn't exist
if not os.path.exists(DATABASE_PATH):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL
            )
        """)
        conn.commit()

# JWT configuration
SECRET_KEY = "your-secret-key-keep-it-secret"  # Change this to a secure random string
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

logger = logging.getLogger(__name__)

def verify_api_key(api_key: str) -> bool:
    """
    Verify if the provided API exists in the database.
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT api_key FROM api_keys WHERE api_key = ?", (api_key,))
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Error verifying API key: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

def insert_api_key(api_key: str, user_id: str) -> bool:
    """
    Insert a new API key into the database.
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO api_keys (api_key, user_id) VALUES (?, ?)",
                (api_key, user_id)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False  # API key already exists
    except sqlite3.Error as e:
        logger.error(f"Error inserting API key: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

def delete_api_key(api_key: str) -> bool:
    """
    Delete an API key from the database.
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM api_keys WHERE api_key = ?", (api_key,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error deleting API key: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
