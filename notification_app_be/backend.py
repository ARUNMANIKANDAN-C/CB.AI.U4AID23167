from datetime import datetime, timedelta
import sqlite3
from sqlite3 import Error
import hashlib
import time

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

DATABASE_PATH = "database.db"

PROTECTED_POST_PATHS = {"/notify_group", "/sort_by_priority"}
API_KEY = "your-secret-api-key"  # Replace with actual key

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


conn = get_db_connection()


def initialize_database():
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'user',
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 0 CHECK (priority BETWEEN 0 AND 10),
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            list_of_user_id TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS new_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            has_new INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (group_id) REFERENCES groups (id)
        );
        """
    )
    conn.commit()


initialize_database()


class LoginPayload(BaseModel):
    email: str
    password: str


class RegisterPayload(LoginPayload):
    name: str
    role: str = "user"


class SortByPriorityPayload(BaseModel):
    user_id: int


class NotifyGroupPayload(BaseModel):
    group_id: int
    message: str


def get_interval_range(dt: datetime, interval_minutes: int = 5):
    interval_start = dt.replace(
        minute=(dt.minute // interval_minutes) * interval_minutes,
        second=0,
        microsecond=0,
    )
    interval_end = interval_start + timedelta(minutes=interval_minutes)
    return interval_start, interval_end


def cleanup_notifications_for_user(user_id: int, interval_minutes: int = 60):
    now = datetime.now()
    interval_start, interval_end = get_interval_range(now, interval_minutes)
    conn.execute(
        "DELETE FROM notifications WHERE user_id = ? AND timestamp >= ? AND timestamp < ?",
        (user_id, interval_start.isoformat(), interval_end.isoformat()),
    )
    conn.commit()


def cleanup_old_notifications(days_to_keep: int = 30):
    cutoff = datetime.now() - timedelta(days=days_to_keep)
    conn.execute("DELETE FROM notifications WHERE timestamp < ?", (cutoff.isoformat(),))
    conn.commit()


@app.get("/")
async def root():
    return {"message": "Notification app backend is running"}

@app.get("/adding_user_to_group")
async def adding_user_to_group():
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    user_id = user[0]
    cursor = conn.execute("SELECT id FROM groups WHERE name = ?", ("<group_name>",))
    group = cursor.fetchone()
    


@app.post("/login")
async def login(payload: LoginPayload):
    cursor = conn.execute("SELECT * FROM users WHERE email = ?", (payload.email,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    stored_password = user[4]
    if hashlib.sha256(payload.password.encode('utf-8')).hexdigest() != stored_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return {"message": "Login successful", "user_id": user[0], "name": user[1], "email": user[2], "role": user[3]}


@app.post("/register")
async def register(payload: RegisterPayload):
    hashed_password = hashlib.sha256(payload.password.encode('utf-8')).hexdigest()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (payload.name, payload.email, hashed_password, payload.role),
        )
        conn.commit()
    except Error as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return {"message": "Registration successful"}


@app.post("/sort_by_priority")
async def sort_by_priority(payload: SortByPriorityPayload):
    cursor = conn.execute(
        "SELECT id, user_id, type, priority, message, timestamp FROM notifications WHERE user_id = ? ORDER BY priority DESC",
        (payload.user_id,),
    )
    notifications = [dict(row) for row in cursor.fetchall()]
    return {"notifications": notifications}


@app.post("/notify_group")
async def notify_group(payload: NotifyGroupPayload):
    cursor = conn.execute("SELECT list_of_user_id FROM groups WHERE id = ?", (payload.group_id,))
    group = cursor.fetchone()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    user_ids = [user_id.strip() for user_id in group[0].split(",") if user_id.strip().isdigit()]
    for user_id in user_ids:
        user_id_int = int(user_id)
        cleanup_notifications_for_user(user_id_int)
        conn.execute(
            "INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)",
            (user_id_int, "group_notification", payload.message),
        )
    conn.commit()
    return JSONResponse({"message": "Group notification sent"}, status_code=status.HTTP_200_OK)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8001)
