import sqlite3
import asyncio
from utils.GuildUtils import GuildUtils
from utils.ErrorHandling import ErrorHandling as EH
from pathlib import Path

class FileSystemUtils:
    
    # File System Navigation
    @staticmethod
    def guild_id_folder(guild_id: int):
        utils_path = Path(__file__).parent
        project_path = Path(utils_path).parent
        guild_id_path = project_path / str(guild_id)
        guild_id_path.mkdir(exist_ok=True)
        return guild_id_path.name
    
    @staticmethod
    def database_folder(guild_id: int):
        utils_path = Path(__file__).parent
        project_path = Path(utils_path).parent
        database_folder_path = project_path / str(guild_id) / "Database"
        database_folder_path.mkdir(exist_ok=True)
        print(f"Created DB directory: '{database_folder_path.name}' in '{database_folder_path.parent.name}'")
        return database_folder_path.name
    
    @staticmethod
    def backup_folder(guild_id: int):
        utils_path = Path(__file__).parent
        project_path = Path(utils_path).parent
        backup_folder_path = project_path / str(guild_id) / "Backups"
        backup_folder_path.mkdir(exist_ok=True)
        print(f"Created backup Directory: '{backup_folder_path.name}' in '{backup_folder_path.parent.name}'")
        return backup_folder_path.name
    