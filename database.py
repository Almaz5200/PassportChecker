import sqlite3
import os
from crawler import CrawlResult


class DatabaseStorage:
    def __init__(self):
        if os.environ.get("RUNNING_IN_DOCKER") == "true":
            self.path = "/app/data/"
        else:
            self.path = "data"

        self.conn = sqlite3.connect(
            os.path.join(self.path, "database.db"), check_same_thread=False
        )
        self.ensure_tables()

    def ensure_tables(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                passport_id TEXT,
                message_id TEXT,
                status TEXT,
                progress TEXT
            )
            """
        )
        self.conn.commit()

    def ensure_user(self, user_id: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
        )
        self.conn.commit()

    def get_users_ids(self):
        return self.conn.execute("SELECT user_id FROM users").fetchall()

    def get(self, user_id: str):
        self.ensure_user(user_id)
        result = self.conn.execute(
            "SELECT passport_id, status, progress FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        return {
            "passport_id": result[0],
            "status": result[1],
            "progress": result[2],
        }

    def set_message_id(self, user_id: str, message_id: str):
        self.ensure_user(user_id)
        self.conn.execute(
            "UPDATE users SET message_id = ? WHERE user_id = ?", (message_id, user_id)
        )
        self.conn.commit()

    def get_message_id(self, user_id: str):
        self.ensure_user(user_id)
        return self.conn.execute(
            "SELECT message_id FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()[0]

    def set_passport_id(self, user_id: str, passport_id: str):
        self.ensure_user(user_id)

        self.conn.execute(
            "UPDATE users SET passport_id = ? WHERE user_id = ?", (passport_id, user_id)
        )
        self.conn.commit()

    def set_info(self, user_id: str, result: CrawlResult):
        self.ensure_user(user_id)
        self.conn.execute(
            "UPDATE users SET status = ?, progress = ? WHERE user_id = ?",
            (result.status, result.progress, user_id),
        )
        self.conn.commit()
