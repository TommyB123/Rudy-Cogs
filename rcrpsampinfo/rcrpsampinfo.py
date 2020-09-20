import discord
import asyncio
import aiomysql
from .config import mysqlconfig
from redbot.core import commands

class RCRPSampInfo(commands.Cog, name="SA-MP Server Info"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.info_task = self.bot.loop.create_task(self.update_samp_info())
    
    async def update_samp_info(self):
        while 1:
            try:
                sql = await aiomysql.connect(**mysqlconfig)
                cursor = await sql.cursor()
                await cursor.execute("SELECT SUM(Online) AS playercount FROM players WHERE Online = 1")
                data = await cursor.fetchone()
                await cursor.close()
                sql.close()

                players = data[0]
                if players == None:
                    players = 0

                game = discord.Game(f'RCRP ({players}/150 players)')
                await self.bot.change_presence(activity = game)
            except:
                pass

            await asyncio.sleep(1) #run every second
    
    def __unload(self):
        self.info_task.cancel()
