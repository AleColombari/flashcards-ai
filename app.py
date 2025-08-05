import sqlite3
import os

from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, request, redirect, url_for, render_template, flash, session
from helpers import login_required, get_or_create_unsorted_folder
from dotenv import load_dotenv
import google.generativeai as genai
from helpers import get_db_connection

#here I used chatgpt-4 help to build the ai related stuff
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

app = Flask(__name__)
app.secret_key = 'dev'


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session.clear()
        username = request.form["username"]
        password = request.form["password"]

        conn= get_db_connection()
        db = conn.cursor()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password!", "error")
            return redirect(url_for("index"))
        
        session["user_id"] = user["id"]
        flash("Logged in successfully!", "success")
        return redirect(url_for("dashboard"))
    
    else:
        return render_template("index.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            db = conn.cursor()
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            flash("Registration successful!", "success")
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "error")
            return redirect(url_for("register"))
        
    else:
        return render_template("register.html")
    
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))
    
@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    conn = get_db_connection()
    db = conn.cursor()
    folders = db.execute("SELECT * FROM folders WHERE user_id = ?", (user_id,)).fetchall()
    unsorted_flashcards = db.execute("SELECT * FROM flashcards WHERE user_id = ? AND folder_id IS NULL ORDER BY created_at DESC", (user_id,)).fetchall()

    conn.close()
    
    return render_template("dashboard.html", folders=folders, flashcards=unsorted_flashcards)


@app.route("/create", methods=["POST"])
@login_required
def create_flashcard():
    user_id = session["user_id"]
    source_text = request.form["source_text"]
    folder_id = request.form.get("folder_id") or get_or_create_unsorted_folder(user_id)

    sumary = generate_sumary(source_text)
    mcq = generate_mcq(source_text)

    conn = get_db_connection()
    db = conn.cursor()

    db.execute("""INSERT INTO flashcards (user_id, front, back, folder_id) VALUES (?, ?, ?, ?)""", (user_id, sumary, mcq, folder_id))

    conn.commit()
    conn.close()

    flash("Flashcard created successfully!", "success")
    return redirect(url_for("dashboard"))

@app.route("/create_folder", methods=["POST"])
@login_required
def create_folder():
    user_id = session["user_id"]
    folder_name = request.form["folder_name"]

    conn = get_db_connection()
    db = conn.cursor()

    existing = db.execute("""SELECT *FROM folders WHERE user_id = ? AND name = ?""", (user_id, folder_name)).fetchone()

    if existing:
        flash("You already have a folder with that name!", "error")
    else:
        db.execute("""INSERT INTO folders (user_id, name) VALUES (?, ?)""", (user_id, folder_name))
        conn.commit()
        flash("Folder created successfully!", "success")

    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/rename_folder/<int:folder_id>", methods=["POST"])
@login_required
def rename_folder(folder_id):
    new_name = request.form["new_name"]
    user_id = session["user_id"]

    conn = get_db_connection()
    db = conn.cursor()

    existing = db.execute("SELECT * FROM folders WHERE user_id = ? AND name = ?", (user_id, new_name)).fetchone()
    if existing:
        flash("You already have a folder with that name!", "error")
    else:
        db.execute("UPDATE folders SET name = ? WHERE id = ? AND user_id = ?", (new_name, folder_id, user_id))
        conn.commit()
        flash("Folder renamed successfully!", "success")

    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/delete_folder/<int:folder_id>", methods=["POST"])
@login_required
def delete_folder(folder_id):
    user_id = session["user_id"]
    conn = get_db_connection()
    db = conn.cursor()

    db.execute("UPDATE flashcards SET folder_id = NULL WHERE folder_id = ? ANd user_id = ?", (folder_id, user_id))
    db.execute("DELETE FROM folders WHERE id = ? AND user_id = ?", (folder_id, user_id))

    conn.commit()
    conn.close()

    flash("Folder deleted successfully!", "success")
    return redirect(url_for("dashboard"))


#i used chatgpt4o to help me build all the ai related stuff in my code, like these two functions and all other needed things so this work

def generate_mcq(text):
    prompt = f"""Based on the following content, write a multiple-choice question with 4 options.
Label the correct answer at the end. Format:

Question: ...
A) ...
B) ...
C) ...
D) ...
Answer: ...

Text:
{text}
"""
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

def generate_sumary(text):
    prompt = f"Summarize the following text for a student who needs to study:\n\n{text}"

    response = gemini_model.generate_content(prompt)
    return response.text.strip()


@app.route("/folder/<int:folder_id>")
@login_required
def view_folder(folder_id):
    index = int(request.args.get("index", 0))
    user_id = session["user_id"]

    conn = get_db_connection()
    db = conn.cursor()

    folder = db.execute("SELECT * FROM folders WHERE id = ? AND user_id = ?", (folder_id, user_id)).fetchone()
    if folder is None:
        flash("Folder not found!", "error")
        return redirect(url_for("dashboard"))
    

    cards = db.execute("SELECT * FROM flashcards WHERE folder_id = ? AND user_id = ? ORDER BY created_at", (folder_id, user_id)).fetchall()
    conn.close()

    if not cards:
        flash("No flashcards in this folder yet.", "info")
        return redirect(url_for("dashboard"))
    
    index = max(0, min(index, len(cards) - 1))
    current_card = cards[index]

    return render_template("folder_view.html", folder=folder, card=current_card, index=index, total=len(cards))


@app.route("/delete_flashcard/<int:card_id>", methods=["POST"])
@login_required
def delete_flashcard(card_id):
    user_id = session["user_id"]
    folder_id = request.args.get("folder_id", type=int)
    index = request.args.get("index", type=int)

    conn = get_db_connection()
    db = conn.cursor()

    db.execute("DELETE FROM flashcards WHERE id = ? AND user_id = ?", (card_id, user_id))
    conn.commit()
    conn.close()

    flash("Flashcard deleted successfully!", "success")
    
    return redirect(url_for("view_folder", folder_id=folder_id, index=max(index -1,0 )))

