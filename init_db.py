"""Create (or upgrade) the local SQLite database for the Projects Tracker.

Run once:  python init_db.py
Safe to run again: if the table already exists it only adds any missing columns.
"""
import sqlite3

conn = sqlite3.connect("tracker.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS Projects (
    Id          INTEGER PRIMARY KEY AUTOINCREMENT,
    SlNo        INTEGER,
    Name        TEXT NOT NULL,
    Owner       TEXT,
    Status      TEXT NOT NULL DEFAULT 'Not Started',
    Consumer    TEXT,
    POC         TEXT,
    DataSource  TEXT,
    UpdateFreq  TEXT,
    TimeUpdate  TEXT,
    Link        TEXT,
    Utilization TEXT,
    StartDate   TEXT,
    DueDate     TEXT,
    Notes       TEXT,
    CreatedAt   TEXT NOT NULL DEFAULT (datetime('now')),
    UpdatedAt   TEXT NOT NULL DEFAULT (datetime('now'))
)
""")

# Upgrade an older tracker.db (from version 1) by adding the new columns
existing = {row[1].lower() for row in cur.execute("PRAGMA table_info(Projects)")}
for col, typ in [("SlNo", "INTEGER"), ("Consumer", "TEXT"), ("POC", "TEXT"), ("DataSource", "TEXT"),
                 ("UpdateFreq", "TEXT"), ("TimeUpdate", "TEXT"), ("Link", "TEXT"), ("Utilization", "TEXT")]:
    if col.lower() not in existing:
        cur.execute(f"ALTER TABLE Projects ADD COLUMN {col} {typ}")
        print("Added column", col)

conn.commit()
count = cur.execute("SELECT COUNT(*) FROM Projects").fetchone()[0]
conn.close()
print(f"Database ready: tracker.db ({count} projects)")
