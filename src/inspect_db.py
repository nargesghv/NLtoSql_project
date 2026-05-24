import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "employees.db"

def inspect_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    print("\nTables:")
    for table in tables:
        print(f"\n--- {table} ---")
        cursor.execute(f"PRAGMA table_info({table});")
        for col in cursor.fetchall():
            print(col)

        print("\nSample rows:")
        cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
        for row in cursor.fetchall():
            print(row)

    conn.close()

if __name__ == "__main__":
    inspect_db()