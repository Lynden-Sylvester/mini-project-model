import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import sqlite3
from typing import List

class CommandSync(commands.Cog):

  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def guild_retreival(self, interaction: discord.Interaction, guild_id, guild_name, fmt):
      db = sqlite3.connect("master.db")

      crsr = db.cursor()

      sql_command = """CREATE TABLE IF NOT EXISTS guild_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER UNIQUE,
        guild_name TEXT NOT NULL,
        master_guild_key TEXT
        );"""

      crsr.execute(sql_command)

      db.commit()
      db.close()


      db = sqlite3.connect("master.db")

      crsr = db.cursor()

      try:
        crsr.execute("""INSERT OR IGNORE INTO guild_profile (guild_id, guild_name, master_guild_key) VALUES (?, ?, ?);""",
                  (guild_id, guild_name, None))
          

        await interaction.response.send_message(f"Server Profile Registered \n Synced {fmt} commands.", ephemeral = True)

      except Exception as e:
        print(e)

      db.commit()
      db.close()

  async def get_all_commands(self):
    all_commands = {}

    # Get global commands
    for command in self.bot.tree.walk_commands():
      if isinstance(command, app_commands.Group):
        subcommands = [sc for sc in command.commands if sc.parent == command]
        all_commands[command.name] = {
          "command": command,
          "subcommands": subcommands
        }
    return all_commands

  
  async def test_format(self, commands, indent_level=1):
    formated_output = []
    indent = '  ' * indent_level
    # List of Elements
    for item in commands:
      # Of type Commad
      await self.of_type_command(item, formated_output, indent)

      # Of Type Group
      if isinstance(item, discord.app_commands.Group):
        formated_output.append(f"\n\n{indent if item.parent is None else indent+indent}{'Sub Group' if (indent_level == 1) and (item.parent is not None) else 'Group'}: {item.name}")
        formated_output.append(f"\n{indent if item.parent is None else indent+indent}Description: {item.description}")

        subcommands = list[item.commands]
        formated_output.append(await CommandSync.test_format(self, [subcommands], indent_level = indent_level + 1))
        
    return ' '.join(formated_output)
  
  async def of_type_command(self, item, formated_output, indent):
    if isinstance(item, discord.app_commands.Command):
        if item.parent is None:
          formated_output.append(f"\n{indent}- {item.name}: {item.description}")
        elif item.parent.parent is None:
          formated_output.append(f"\n{indent*2}- {item.name}: {item.description}")
        else:
          formated_output.append(f"\n{indent*3}- {item.name}: {item.description}")
  
  @app_commands.command(name="sync", description="Dev Command to Sync all Commands")
  @app_commands.guilds(discord.Object(id=(os.getenv('GUILD_ID'))))
  async def slash_sync(self, interaction: discord.Interaction) -> None:
    guild_id = interaction.guild.id
    guild_name = interaction.guild.name
    global_commands = await interaction.client.tree.sync()
    guild_specific = await interaction.client.tree.sync(guild=interaction.guild)
    fmt = len(global_commands) + len(guild_specific)
    await self.guild_retreival(interaction, guild_id, guild_name, fmt)
    
    global_application_commands = self.bot.tree.walk_commands()
    print(f"\nCommand List: \n{await CommandSync.test_format(self, global_application_commands)}")
  

  
  @commands.command()
  async def sync(self, ctx) -> None:

    guild_id = ctx.guild.id
    guild_name = ctx.guild.name

    

    fmt = await ctx.bot.tree.sync(guild=ctx.guild)

    await self.guild_retreival(ctx, guild_id, guild_name, fmt)

    await ctx.send(f'Synced {len(fmt)} commands.')
    print(f'Synced {len(fmt)} commands.')

async def setup(bot):
  await bot.add_cog(CommandSync(bot))
  print('CommandSync Cog Loaded')
