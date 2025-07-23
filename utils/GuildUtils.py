import sqlite3
from pathlib import Path

class GuildUtils:

    @staticmethod
    def get_guild_name(guild_id: int):
        with sqlite3.connect("master.db") as db:
            crsr = db.cursor()
            crsr.execute("SELECT guild_name FROM guild_profile WHERE guild_id=?", (guild_id, ))
            guild_name = crsr.fetchone()
            if guild_name:
                return guild_name[0]
            else:
                return None
            
    @staticmethod
    def get_guild_profiles():
        with sqlite3.connect("master.db") as db:
            crsr = db.cursor()
            crsr.execute("SELECT * FROM guild_profile;")
            rows = crsr.fetchall()
            return rows
    