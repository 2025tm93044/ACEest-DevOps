import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, redirect, render_template_string, request, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["DATABASE"] = os.environ.get("DATABASE_PATH", str(Path(__file__).with_name("aceest.db")))

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ACEest Fitness &amp; Gym</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #172033; background: #f5f7fb; }
    h1 { color: #153e75; } section { background: white; padding: 1rem 1.25rem; margin: 1rem 0; border-radius: 10px; box-shadow: 0 2px 8px #0001; }
    input, button { padding: .65rem; margin: .25rem 0; } input { max-width: 100%; box-sizing: border-box; } button { background: #176b55; color: white; border: 0; border-radius: 5px; cursor: pointer; }
    .flash { padding: .6rem; background: #fff3cd; border-radius: 5px; } li { margin: .35rem 0; }
  </style>
</head>
<body>
  <h1>ACEest Fitness &amp; Gym</h1>
  <p>Simple member and workout tracker for the ACEest gym.</p>
  {% with messages = get_flashed_messages() %}
    {% for message in messages %}<p class="flash">{{ message }}</p>{% endfor %}
  {% endwith %}
  <section>
    <h2>Register a member</h2>
    <form method="post" action="{{ url_for('add_member') }}">
      <label>Name <input name="name" required maxlength="100"></label>
      <label>Email <input name="email" type="email" required maxlength="254"></label>
      <button type="submit">Add member</button>
    </form>
  </section>
  <section>
    <h2>Log a workout</h2>
    <form method="post" action="{{ url_for('add_workout') }}">
      <label>Member
        <select name="member_id" required>
          {% for member in members %}<option value="{{ member['id'] }}">{{ member['name'] }} ({{ member['email'] }})</option>{% endfor %}
        </select>
      </label>
      <label>Workout <input name="activity" required maxlength="100" placeholder="e.g. Strength training"></label>
      <label>Minutes <input name="minutes" type="number" min="1" max="600" required></label>
      <button type="submit">Log workout</button>
    </form>
  </section>
  <section>
    <h2>Members</h2>
    {% if members %}<ul>{% for member in members %}<li>{{ member['name'] }} — {{ member['email'] }}</li>{% endfor %}</ul>{% else %}<p>No members yet. Register the first member above.</p>{% endif %}
  </section>
  <section>
    <h2>Recent workouts</h2>
    {% if workouts %}<ul>{% for workout in workouts %}<li>{{ workout['name'] }}: {{ workout['activity'] }} — {{ workout['minutes'] }} minutes</li>{% endfor %}</ul>{% else %}<p>No workouts logged yet.</p>{% endif %}
  </section>
</body>
</html>
"""


def get_db():
    """Open a SQLite connection and ensure the schema exists."""
    database = app.config["DATABASE"]
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            activity TEXT NOT NULL,
            minutes INTEGER NOT NULL CHECK(minutes > 0),
            FOREIGN KEY(member_id) REFERENCES members(id)
        )"""
    )
    connection.commit()
    return connection


@app.get("/")
def index():
    with get_db() as connection:
        members = connection.execute("SELECT * FROM members ORDER BY name").fetchall()
        workouts = connection.execute(
            """SELECT workouts.*, members.name
               FROM workouts JOIN members ON members.id = workouts.member_id
               ORDER BY workouts.id DESC LIMIT 10"""
        ).fetchall()
    return render_template_string(PAGE, members=members, workouts=workouts)


@app.post("/members")
def add_member():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    if not name or not email:
        flash("Name and email are required.")
        return redirect(url_for("index"))
    try:
        with get_db() as connection:
            connection.execute(
                "INSERT INTO members (name, email) VALUES (?, ?)", (name, email)
            )
        flash("Member registered successfully.")
    except sqlite3.IntegrityError:
        flash("That email is already registered.")
    return redirect(url_for("index"))


@app.post("/workouts")
def add_workout():
    activity = request.form.get("activity", "").strip()
    try:
        member_id = int(request.form.get("member_id", ""))
        minutes = int(request.form.get("minutes", ""))
    except ValueError:
        flash("Choose a member and enter a valid number of minutes.")
        return redirect(url_for("index"))
    if not activity or not 1 <= minutes <= 600:
        flash("Workout name is required and minutes must be between 1 and 600.")
        return redirect(url_for("index"))
    try:
        with get_db() as connection:
            connection.execute(
                "INSERT INTO workouts (member_id, activity, minutes) VALUES (?, ?, ?)",
                (member_id, activity, minutes),
            )
        flash("Workout logged successfully.")
    except sqlite3.IntegrityError:
        flash("The selected member does not exist.")
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
