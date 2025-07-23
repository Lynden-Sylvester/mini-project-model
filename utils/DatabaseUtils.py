import discord 
import sqlite3
from pathlib import Path
from typing import Optional
import shutil
from datetime import datetime
from utils.GuildUtils import GuildUtils
from utils.FileSystemUtils import FileSystemUtils as FSU
import re
import os
import discord

class DatabaseUtils:

    @staticmethod
    def get_table_schema(db_path: str, table_name: str):
        try:
            with sqlite3.connect(db_path) as conn:
                crsr = conn.cursor()
                crsr.execute(f"""PRAGMA table_info({table_name})""")
                schema = [[row[1], row[2], row[4]] for row in crsr.fetchall()]
                return schema
        except sqlite3.Error as e:
            print(f"Error getting Schema: {e}")
            return None
        
    @staticmethod
    def create_database(db_path, db_name, guild: discord.Guild) -> Optional[discord.Guild]:
        guild_id = guild
        print(f"Path: {Path(db_path)}")
        print(Path(__file__))
        print(f"{Path(Path(db_path) / f'{db_name}.db').exists() == False}")
        print(f"{db_name != 'Guild'}")
        
        if ((db_name == "Guild") and (Path(Path(db_path) / "Guild.db").exists() ==  False)) == True:
            created_guild_database_path = Path(db_path) / "Guild.db"
            print(f"Created Guild DB Path: {created_guild_database_path}")
            print(f"DB name: {created_guild_database_path.name}")
            sqlite3.connect(created_guild_database_path)
            print(f"DB path: {db_path}")
            print(f"Created DB path: {created_guild_database_path}")
            print(f"DB Name: {db_name}")
            return created_guild_database_path
        else:
            database = Path(db_path) / f"{db_name}.db"
            full_db_path = Path(str(guild_id)) / database
            print(f"Db path: {full_db_path}")
            sqlite3.connect(f"{full_db_path}")
            print(f"Database {database.name} created in '{db_path}'")
            return database
        
    @staticmethod
    def initial_backup_database(db_name, db_path, guild_id):
        backup_file = f"{db_name}_init_{datetime.now().strftime('%Y-%b-%d %H:%M:%S')}.db"
        database_backup_path = Path(db_path) / backup_file
        print(database_backup_path)
        guild_folder = FSU.guild_id_folder(guild_id)

        sqlite3.connect(Path(guild_folder) / database_backup_path)
        print(f"Initial backup created: {database_backup_path}")
        return database_backup_path

    # Get latest backup
    @staticmethod
    def get_latest_backup_path(backup_path):
        latest_backup = None
        latest_timestamp = 0
        print(f"backup_path: {backup_path}")
        for filename in Path.iterdir(backup_path):
            timestamp = Path(filename).stat().st_mtime
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_backup = filename
        return latest_backup
    
    # Perform a Differential backup
    @staticmethod
    def differential_backup(source_database_path, backup_path):
        latest_backup_path = DatabaseUtils.get_latest_backup_path(backup_path)
        print(f"Latest backup path: {latest_backup_path}")
        if not latest_backup_path:
            print(f"[{datetime.now().strftime('%Y-%b-%d %H:%M:%S')}] No previous backup found. Creating a Full backup.")
            return DatabaseUtils.full_backup(source_database_path, backup_path)
        
        latest_backup_timestamp = Path(latest_backup_path).stat().st_mtime
        source_db_timestamp = Path(source_database_path).stat().st_mtime

        if source_db_timestamp <= latest_backup_timestamp:
            print(f"[{datetime.now().strftime('%Y-%b-%d %H:%M:%S')}] No changes detected {f'{Path(source_database_path).name}'} --> Skipping backup")
            return False
        
        else:
            backup_name = f"{Path(source_database_path).name.rsplit('.')[0]}_diff_{datetime.now().strftime('%y-%b-%d %H:%M:%S')}.db"
            backup_path_file = Path(backup_path) / backup_name
            print(f"Source DB: {source_database_path}")
            print(f"Source DB name: {Path(source_database_path).name}")
            with sqlite3.connect(Path(source_database_path)) as source_conn, sqlite3.connect(latest_backup_path) as backup_conn:
                source_crsr = source_conn.cursor()
                backup_crsr = backup_conn.cursor()

                source_crsr.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = source_crsr.fetchall()

                for table_name in tables:
                    table_name = table_name[0]
                    source_crsr.execute(f"SELECT * FROM {table_name}")
                    rows = source_crsr.fetchmany(1000)

                    while rows:
                        backup_crsr.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name= '{table_name}'")
                        if backup_crsr.fetchone():
                            backup_crsr.execute(f"DELETE FROM {table_name}")
                            backup_conn.commit()
                            backup_crsr.executemany(f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(rows[0]))})", rows)
                            backup_conn.commit()

                        else:
                            source_crsr(f"PRAGMA table_info ('{table_name})')")
                            result = source_crsr.fetchall()
                            columns = result[1]
                            datatypes = result[2]
                            backup_crsr.execute(f"CREATE TABLE '{table_name}' ({', '.join([f'{col} {datatypes[i]}' for i, col in enumerate(result)])})")
                            backup_conn.commit()
                            backup_crsr.executemany(f"INSERT INTO {table_name} VALUES ({','.join['?'] * len(columns)})", rows)
                            backup_conn.commit()

            shutil.copy2(source_database_path, backup_path_file)
            print(f"[{datetime.now().strftime('%Y-%b-%d %H:%M:%S')}] differential backup created: {backup_path_file}")
            return backup_path_file

    # Perform a Full backup
    @staticmethod
    def full_backup(source_database_path, backup_path):
        backup_name = f"{Path(source_database_path).name.rsplit('.')[0]}_full_{datetime.now().strftime('%Y-%b-%d %H:%M:%S')}.db"
        guild_id = Path(source_database_path).parent.name
        print(f"backup_path: {backup_path}")
        print(f"guild_id: {guild_id}")
        backup_path_file = Path(Path(guild_id) / Path(backup_path)) / backup_name
        print(f"backup_path_file: {backup_path_file}")
        print(f"Source: {source_database_path}")
        shutil.copy2(source_database_path, backup_path_file)
        print(f"[{datetime.now().strftime('%Y-%b-%d %H:%M:%S')}] Full backup created: {backup_path_file}")
        return backup_path_file
    
    # database Integrity Check
    @staticmethod
    def check_database_integrity(database_path):
        db = sqlite3.connect(Path(database_path).name)
        crsr = db.cursor()
        crsr.execute("PRAGMA integrity_check;")
        result = crsr.fetchone()
        if result.__contains__('ok'):
            print("Datbase integrity check passed")
        else:
            print(f"Dtabase integrity check failed: {result}")
        db.close()

    @staticmethod
    def validate_input(value: str, type_: str) -> bool:
        if (type_ == "table_name") or (type_ == "column_name"):
            return bool(re.match(r'^[a-zA-Z_][\w]{0,30}$', value))
        else:
            return False
