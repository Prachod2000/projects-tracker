import sqlite3
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")
DB = "tracker.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row   # lets us turn rows into dicts
    return conn


# ---------- Serve the web page ----------
@app.route("/")
def home():
    return send_from_directory("static", "index.html")


# ---------- API: list all projects ----------
@app.route("/api/projects", methods=["GET"])
def list_projects():
    conn = get_db()
    rows = conn.execute("SELECT * FROM Projects ORDER BY Id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ---------- API: add a project ----------
@app.route("/api/projects", methods=["POST"])
def add_project():
    data = request.get_json()
    if not data or not data.get("Name"):
        return jsonify({"error": "Name is required"}), 400

    conn = get_db()
    cur = conn.execute(
        """INSERT INTO Projects (Name, Owner, Status, StartDate, DueDate, Notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (data.get("Name"), data.get("Owner"), data.get("Status", "Not Started"),
         data.get("StartDate"), data.get("DueDate"), data.get("Notes")),
    )
    conn.commit()
    new_id = cur.lastrowid
    row = conn.execute("SELECT * FROM Projects WHERE Id = ?", (new_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


# ---------- API: update a project ----------
@app.route("/api/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    data = request.get_json()
    if not data or not data.get("Name"):
        return jsonify({"error": "Name is required"}), 400

    conn = get_db()
    conn.execute(
        """UPDATE Projects
           SET Name = ?, Owner = ?, Status = ?, StartDate = ?, DueDate = ?, Notes = ?,
               UpdatedAt = datetime('now')
           WHERE Id = ?""",
        (data.get("Name"), data.get("Owner"), data.get("Status"),
         data.get("StartDate"), data.get("DueDate"), data.get("Notes"), project_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM Projects WHERE Id = ?", (project_id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))


# ---------- API: delete a project ----------
@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    conn = get_db()
    conn.execute("DELETE FROM Projects WHERE Id = ?", (project_id,))
    conn.commit()
    conn.close()
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
