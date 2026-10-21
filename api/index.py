import os
import sqlite3
import datetime
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATABASE_URL = os.environ.get("DATABASE_URL")   # set on Vercel (Neon); absent locally -> SQLite

app = Flask(__name__, static_folder=os.path.join(ROOT, "public"), static_url_path="")

COLS = ["Id", "Name", "Owner", "Status", "StartDate", "DueDate", "Notes", "CreatedAt", "UpdatedAt"]
KEYMAP = {c.lower(): c for c in COLS}


# ---------- Database helpers (SQLite locally, Postgres on Vercel) ----------
def get_conn():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    conn = sqlite3.connect(os.path.join(ROOT, "tracker.db"))
    conn.row_factory = sqlite3.Row
    return conn


def norm(row):
    """Turn a DB row into a dict with consistent CamelCase keys and JSON-safe values."""
    out = {}
    for k, v in dict(row).items():
        if isinstance(v, (datetime.date, datetime.datetime)):
            v = v.isoformat()
        out[KEYMAP.get(k.lower(), k)] = v
    return out


def run(sql, params=(), fetch=None, returning_id=False):
    """Execute SQL on whichever database is configured. fetch = 'one' | 'all' | None."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        if DATABASE_URL:
            sql = sql.replace("?", "%s")
            if returning_id:
                sql += " RETURNING id"
        cur.execute(sql, params)
        result = None
        if returning_id:
            result = cur.fetchone()["id"] if DATABASE_URL else cur.lastrowid
        elif fetch == "one":
            r = cur.fetchone()
            result = norm(r) if r else None
        elif fetch == "all":
            result = [norm(r) for r in cur.fetchall()]
        conn.commit()
        return result
    finally:
        conn.close()


# ---------- Web page (used when running locally) ----------
@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# ---------- API ----------
@app.route("/api/projects", methods=["GET"])
def list_projects():
    return jsonify(run("SELECT * FROM Projects ORDER BY Id DESC", fetch="all"))


@app.route("/api/projects", methods=["POST"])
def add_project():
    data = request.get_json()
    if not data or not data.get("Name"):
        return jsonify({"error": "Name is required"}), 400
    new_id = run(
        """INSERT INTO Projects (Name, Owner, Status, StartDate, DueDate, Notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (data.get("Name"), data.get("Owner"), data.get("Status", "Not Started"),
         data.get("StartDate"), data.get("DueDate"), data.get("Notes")),
        returning_id=True,
    )
    return jsonify(run("SELECT * FROM Projects WHERE Id = ?", (new_id,), fetch="one")), 201


@app.route("/api/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    data = request.get_json()
    if not data or not data.get("Name"):
        return jsonify({"error": "Name is required"}), 400
    run(
        """UPDATE Projects
           SET Name = ?, Owner = ?, Status = ?, StartDate = ?, DueDate = ?, Notes = ?,
               UpdatedAt = CURRENT_TIMESTAMP
           WHERE Id = ?""",
        (data.get("Name"), data.get("Owner"), data.get("Status"),
         data.get("StartDate"), data.get("DueDate"), data.get("Notes"), project_id),
    )
    row = run("SELECT * FROM Projects WHERE Id = ?", (project_id,), fetch="one")
    if row is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(row)


@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    run("DELETE FROM Projects WHERE Id = ?", (project_id,))
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
