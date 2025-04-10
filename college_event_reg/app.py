from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize database (only runs once)
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            event_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM events")
    events = c.fetchall()
    conn.close()
    return render_template("home.html", events=events)

@app.route("/create_event", methods=["GET", "POST"])
def create_event():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        date = request.form["date"]
        c.execute("INSERT INTO events (title, description, date) VALUES (?, ?, ?)",
                  (title, description, date))
        conn.commit()
        conn.close()
        return redirect("/")
    
    conn.close()
    return render_template("event_form.html")

@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register(event_id):
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO registrations (name, email, event_id) VALUES (?, ?, ?)",
                  (name, email, event_id))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        SELECT registrations.name, registrations.email, events.title
        FROM registrations
        JOIN events ON registrations.event_id = events.id
    """)
    registrations = c.fetchall()
    conn.close()
    return render_template("dashboard.html", registrations=registrations)

@app.route("/clear_registrations")
def clear_registrations():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM registrations")
    conn.commit()
    conn.close()
    return redirect("/dashboard")  # Redirects to dashboard

@app.route("/clear_events")
def clear_events():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM events")
    c.execute("DELETE FROM registrations")  # Also clear registrations to avoid foreign key issues
    conn.commit()
    conn.close()
    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)
