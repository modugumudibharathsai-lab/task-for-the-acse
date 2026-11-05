import sqlite3

def add_tables():
    db_path = r"database\vigbot.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS studentlife_grievance (
            tracking_id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS studentlife_club_application (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            club_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(club_id) REFERENCES studentlife_club(club_id)
        )
    """)
    
    conn.commit()
    print("Grievance and Club Application tables created successfully.")
    conn.close()

if __name__ == "__main__":
    add_tables()
