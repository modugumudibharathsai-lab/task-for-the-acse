import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "..", "database", "vigbot.db")

def migrate():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    tables_to_alter = [
        "studentlife_club_member",
        "studentlife_club_application",
        "studentlife_grievance"
    ]

    for table in tables_to_alter:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN student_id TEXT DEFAULT '251FA04E13'")
            print(f"Added student_id to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"student_id already exists in {table}")
            else:
                print(f"Error altering {table}: {e}")

    # Create library_lended_books
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS library_lended_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                book_title TEXT NOT NULL,
                issued_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        print("Created library_lended_books table")
    except Exception as e:
        print(f"Error creating library_lended_books: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
