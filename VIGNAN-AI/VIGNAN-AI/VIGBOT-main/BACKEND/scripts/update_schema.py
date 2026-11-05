import sqlite3

db_path = r"database\vigbot.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column(table, column_name, data_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {data_type}")
        print(f"Added {column_name} to {table}")
    except sqlite3.OperationalError as e:
        print(f"Error (or column already exists) for {table}: {e}")

add_column("studentlife_grievance", "withdrawal_reason", "TEXT")
add_column("studentlife_club_application", "withdrawal_reason", "TEXT")

conn.commit()
conn.close()
