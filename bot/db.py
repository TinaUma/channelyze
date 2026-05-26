import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "orders.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                service_name TEXT NOT NULL,
                client_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                birth_time TEXT NOT NULL,
                birth_place TEXT NOT NULL,
                payment_screenshot_id TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)


def save_order(
    user_id: int,
    username: str | None,
    service_name: str,
    client_name: str,
    birth_date: str,
    birth_time: str,
    birth_place: str,
    payment_screenshot_id: str | None = None,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO orders
                (user_id, username, service_name, client_name,
                 birth_date, birth_time, birth_place, payment_screenshot_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                username,
                service_name,
                client_name,
                birth_date,
                birth_time,
                birth_place,
                payment_screenshot_id,
            ),
        )
        return cursor.lastrowid


def get_order(order_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
