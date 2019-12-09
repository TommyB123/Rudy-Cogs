import discord
import asyncio
import aiomysql
from cogs.mysqlinfo import mysqlconfig
from discord.ext import commands

class SampinfoCog(commands.Cog, name="SA-MP Server Info"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(UpdateSAMPInfo(self))

async def UpdateSAMPInfo(self):
    while 1:
        try:
            sql = await aiomysql.connect(** mysqlconfig)
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
            print("Error while updating player count.")

        await asyncio.sleep(1) #run every second

def setup(bot):
    bot.add_cog(SampinfoCog(bot))