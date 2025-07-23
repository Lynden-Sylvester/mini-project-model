import sqlite3

class AdminUtils:
    def __init__(self, bot):
        self.bot = bot

    # Add Admin Users
    @staticmethod
    def add_admin_to_guild(username, server_database):
        with sqlite3.connect(f"{server_database}") as conn:
            crsr = conn.cursor()
            print(f"{server_database}")
            crsr.execute("""CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            user_id INT UNIQUE);""")
            conn.commit()
            crsr.execute("INSERT OR IGNORE INTO admin (username, user_id) VALUES (?, ?)", (username.name, username.id))
            conn.commit()

    # Remove Admin Users
    @staticmethod
    def remove_admin_from_guild(username, db_path):
        with sqlite3.connect(f"{db_path}") as conn:
            crsr = conn.cursor()

            crsr.execute("DELETE FROM admin WHERE username = ? AND user_id = ?", (username.name, username.id))
            conn.commit()

    @staticmethod
    def guild_database_job_ids_table(job_id, db_name, server_database):
        with sqlite3.connect(f"{server_database}") as conn:
            crsr = conn.cursor()
            print(f"{server_database}")
            crsr.execute("""CREATE TABLE IF NOT EXISTS guild_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            db_name TEXT NOT NULL,
            job_id VARCHAR UNIQUE);""")
            conn.commit()
            crsr.execute("INSERT OR IGNORE INTO guild_jobs (db_name, job_id) VALUES (?, ?)", (db_name, job_id))
            conn.commit()