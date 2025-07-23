import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content= True

        super().__init__(command_prefix="#", intents=intents, application_id=os.getenv("APP_ID"))

    async def on_ready(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = f"cogs.{filename[:-3]}"
                if cog_name not in bot.cogs:
                    try:
                        await bot.load_extension(cog_name)
                        print(f"Loaded cog: {cog_name}")
                    except Exception as e:
                        if e != commands.ExtensionAlreadyLoaded:
                            print(f"{cog_name} - {e}")
                            raise e

load_dotenv()

bot = Bot()
token = os.getenv('BOT_SECRET')
bot.run(token)