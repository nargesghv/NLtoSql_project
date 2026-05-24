import sqlite3
from tabulate import tabulate
from config import DB_PATH

def get_schema_text() -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    parts = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        col_lines = [f"- {col[1]} {col[2]}" for col in columns]
        parts.append(f"Table: {table}\n" + "\n".join(col_lines))

    conn.close()
    return "\n\n".join(parts)

def execute_sql(sql: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description] if cursor.description else []
    conn.close()
    return headers, rows

def format_results(headers, rows) -> str:
    if not rows:
        return "No results found for the selected department."
    return tabulate(rows, headers=headers, tablefmt="grid")