import sqlite3

conn = sqlite3.connect("tracker.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS Projects (
    Id         INTEGER PRIMARY KEY AUTOINCREMENT,
    Name       TEXT NOT NULL,
    Owner      TEXT,
    Status     TEXT NOT NULL DEFAULT 'Not Started',
    StartDate  TEXT,
    DueDate    TEXT,
    Notes      TEXT,
    CreatedAt  TEXT NOT NULL DEFAULT (datetime('now')),
    UpdatedAt  TEXT NOT NULL DEFAULT (datetime('now'))
)
""")

cur.execute("""
INSERT INTO Projects (Name, Owner, Status, StartDate, DueDate, Notes)
VALUES ('Sample Project', 'Prachod', 'In Progress', '2026-10-01', '2026-11-30', 'First test row')
""")

conn.commit()

for row in cur.execute("SELECT * FROM Projects"):
    print(row)

conn.close()
print("Database ready: tracker.db")
