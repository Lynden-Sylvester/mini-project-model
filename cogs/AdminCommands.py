import apscheduler.job
import apscheduler.schedulers
import apscheduler.schedulers.asyncio
import apscheduler.schedulers.base
import discord
from discord import app_commands
from discord.ext import commands, tasks
import sqlite3
import os
import asyncio
import aiofiles
from datetime import datetime, timedelta
import shutil
from typing import Optional
from discord.ui import View, Button
import csv
from io import StringIO
import yaml
import datetime
from dotenv import load_dotenv
from pathlib import Path
import re
import apscheduler
from apscheduler.triggers.cron import CronTrigger
from utils.ErrorHandling import ErrorHandling as EH
from utils.AdminUtils  import AdminUtils
from discord_modules.ConfirmView import ConfirmView as ConfirmView
from utils.GuildUtils import GuildUtils
from utils.DatabaseUtils import DatabaseUtils
from utils.AdminUtils import AdminUtils
from utils.FileSystemUtils import FileSystemUtils as FSU
from main import scheduler

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    admin_perms = discord.Permissions(administrator=True)

    # Admin Group
    admin = app_commands.Group(name='admin', description="Admin Commands", default_permissions=admin_perms)

    # Initialize Server Profile
    @admin.command(name="guild_init", description="Creates Guild Profile")
    async def guild_init(self, interaction: discord.Interaction, guild_key: str):
        guild_id = interaction.guild.id
        if (interaction.user.get_role(int(os.getenv("ADMIN_ROLE_ID")))):
            db = sqlite3.connect("master.db")
            crsr = db.cursor()
            crsr.execute("SELECT guild_id, guild_name FROM guild_profile WHERE guild_id=?", (guild_id,))
            db.commit()
            crsr.fetchone()
            crsr.execute("UPDATE guild_profile SET master_guild_key = ? WHERE guild_id = ?", (guild_key, guild_id))
            db.commit()
            
            profile_list_strf = ""
            guild_profile = crsr.execute("SELECT * FROM guild_profile WHERE guild_id =?", (guild_id,))
            for row in guild_profile:
                profile_list_strf += f'Guild ID: **{row[1]}** | Guild Name: *{row[2]}* | Guild Key: __{row[3]}__ \n'
            guild_name = await asyncio.to_thread(GuildUtils.get_guild_name, guild_id)
            base_path = await asyncio.to_thread(FSU.guild_id_folder, guild_id)
            print(f"Created Directory: {base_path}")
            await asyncio.to_thread(FSU.database_folder, guild_id)
            backups_path = await asyncio.to_thread(FSU.backup_folder, guild_id)
            print(f"This is backups_paths: {backups_path}")
            guild_database = await asyncio.to_thread(DatabaseUtils.create_database, base_path, "Guild", interaction.guild)
            guild_database_initial_backup = await asyncio.to_thread(DatabaseUtils.initial_backup_database, "Guild", backups_path, guild_id)
            db.close()
            job = scheduler.add_job(DatabaseUtils.full_backup,  'cron', day='*/1', id=str(guild_id), args=(guild_database, backups_path))
            print(f"This is the db: {guild_database}")
            guild_db = sqlite3.connect(guild_database)
            guild_crsr = guild_db.cursor()
            guild_crsr.execute("""CREATE TABLE IF NOT EXISTS guild_jobs (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               db_name TEXT NOT NULL,
                               job_id VARCHAR UNIQUE);""")


            em = discord.Embed(title="Guild Profile - DO NOT SHARE", description=f"{profile_list_strf}")
            em.add_field(name="Created Guild Database", value=f"{guild_database}")
            em.add_field(name="Guild Database Backup", value=f"{guild_database_initial_backup}")

            # Source File Path
            source_settings_file = Path(Path(__file__).parent.parent) / "configs" / 'settings.yml'
            dest_settings_file = Path(base_path) / 'settings.yml'

            shutil.copy2(source_settings_file, dest_settings_file)

            # Read the source YAML file
            async with aiofiles.open(source_settings_file, 'r') as source_file:
               modified_lines = []
               async for line in source_file:
                if line.strip().startswith('guild_key:'):
                    modified_lines.append(f' guild_key: {guild_key}\n')
                elif line.strip().startswith('guild_name:'):
                    modified_lines.append(f' guild_name: {guild_name}\n')
                elif line.strip().startswith('guild_id:'):
                    modified_lines.append(f' guild_id: {guild_id}\n')
                elif line.strip().startswith('guild_job_id:'):
                    modified_lines.append(f' guild_job_id: {job.id}\n')
                else:
                    modified_lines.append(line)
    
            # Write the modified content to the destination file
            async with aiofiles.open(dest_settings_file, 'w') as dest_file:
               await dest_file.writelines(modified_lines)

            await interaction.response.send_message(embed=em, ephemeral=True)
        else:
            await interaction.response.send_message("Access Denied", ephemeral=True)

    # DB Management
    @admin.command(name="db", description="Database Management")
    @app_commands.describe(option="Choose an option")
    @app_commands.choices(option=[
        app_commands.Choice(name="Create", value=1),
        app_commands.Choice(name="Delete", value=2),
        app_commands.Choice(name="Backup", value=3),
        app_commands.Choice(name="Integrity", value=4)
        ])
    async def db_management(self, interaction: discord.Interaction, option: app_commands.Choice[int], db_name: str, delete_backups: Optional[bool] = None) -> None:
        guild_id = interaction.guild.id
        
        guild_name = await asyncio.to_thread(GuildUtils.get_guild_name, guild_id)
        await asyncio.to_thread(EH.is_not_none, "guild_name", guild_name)

        base_path = await asyncio.to_thread(FSU.guild_id_folder, guild_id)
        await asyncio.to_thread(EH.is_not_none, "base_path", base_path)
                
        database_path = await asyncio.to_thread(FSU.database_folder, guild_id)
        await asyncio.to_thread(EH.is_not_none, "database_path", database_path)
        print(f"This is database_path XXXXXXXX: {database_path}")
        
        
        if option.value == 1:

            database_folder = await asyncio.to_thread(DatabaseUtils.create_database, database_path, db_name, guild_id)
            full_database_path = Path(Path(__file__).parent).parent / database_folder / "Database" / f"{db_name}.db"
            backups_path = Path(Path(__file__).parent).parent / str(guild_id) / "Backups"
            guild_database = Path(Path(__file__).parent).parent / str(guild_id) / "Guild.db"
            print(f"this is backups_path: {backups_path}")
            await asyncio.to_thread(EH.is_not_none, "backups_path", backups_path)

            await asyncio.to_thread(DatabaseUtils.initial_backup_database, db_name, backups_path, guild_id)
            job = scheduler.add_job(DatabaseUtils.full_backup, 'cron', day='*/1', args=(full_database_path, backups_path))
            print(f"job: {job} and job.id: {job.id}")
            
            # THIS LINE HERE 
            await asyncio.to_thread(AdminUtils.guild_database_job_ids_table(job.id, db_name, guild_database))

            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Created database named: {db_name}", ephemeral=True)

        if option.value == 2:
            if delete_backups is None:
                await interaction.response.send_message("Must include 'delete_backups' parameter")
            main_database_path = str(guild_id) / Path(database_path) / f"{db_name}.db"
            backups_folder = await asyncio.to_thread(FSU.backup_folder, guild_id)
            backups_path = Path(Path(__file__).parent).parent / str(guild_id) / str(backups_folder)
            await asyncio.to_thread(EH.is_not_none, "backups_path", backups_path)

            confirm_view = ConfirmView(interaction)
            # Create confirmation message
            await interaction.response.send_message(f"Are you sure you want to delete the database `{db_name}`?", view=confirm_view, ephemeral=True)
            # Wait for the view to timeout or be stopped
            await confirm_view.wait()
            if confirm_view.value is True:
                try:
                    # Delete main database file
                    if Path(main_database_path).exists():
                        os.remove(main_database_path)
                        await interaction.followup.send(f"Database `{db_name}` deleted successfully.", ephemeral=True)
                    # Delete backup files if requested
                    if delete_backups:
                        print(f"This is backups_path: {backups_path}")
                        if Path(backups_path).is_dir():
                            for filename in os.listdir(backups_path):
                                if (filename.__contains__(db_name) and filename.endswith(".db")):
                                    os.remove(Path(backups_path) / filename)
                            os.remove(f"{main_database_path}.db")
                            await interaction.followup.send("Backup files deleted successfully.", ephemeral=True)
                        else:
                            await interaction.followup.send("No backup directory found.", ephemeral=True)
                except Exception as e:
                        await interaction.followup.send(f"An error occurred during deletion: {str(e)}", ephemeral=True)
            else:
                await asyncio.to_thread(EH.confirm_view_handling, confirm_view.value, interaction)

        if option.value == 3:

            main_database_path = str(guild_id) / Path(database_path) / f"{db_name}.db"
            backups_path = await asyncio.to_thread(FSU.backup_folder, guild_id)
            await asyncio.to_thread(EH.is_not_none, "backups_path", backups_path)
            backup_file = await asyncio.to_thread(DatabaseUtils.full_backup,  main_database_path, backups_path)
            shutil.copy2(main_database_path, backup_file)
            await interaction.response.send_message(f"Manually created backup located at: `{backup_file}`", ephemeral=True)

        if option.value == 4:

            full_database_path = Path(database_path) / f"{db_name}.db"
            health = await asyncio.to_thread(DatabaseUtils.check_database_integrity, full_database_path)
            if ((health == 'ok') or (health is None)):
                await interaction.response.send_message(f"Database {db_name} health is good", ephemeral=True)
            else:
                await interaction.response.send_message(f"Database {db_name} health is {health}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))