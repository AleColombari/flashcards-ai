from functools import wraps
from flask import redirect, url_for, session, flash
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("flashcards.db")
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You need to be logged in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def get_or_create_unsorted_folder(user_id):
    conn = get_db_connection()
    db = conn.cursor()

    folder = db.execute("""
        SELECT * FROM folders WHERE user_id = ? AND name = 'New Flashcards'
    """, (user_id,)).fetchone()

    if folder is None:
        db.execute("""
            INSERT INTO folders (user_id, name) VALUES (?, ?)
        """, (user_id, "New Flashcards"))
        conn.commit()
        folder = db.execute("""
            SELECT * FROM folders WHERE user_id = ? AND name = 'New Flashcards'
        """, (user_id,)).fetchone()

    conn.close()
    return folder["id"]
