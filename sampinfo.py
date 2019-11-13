import discord
import mysql.connector
from mysqlinfo import mysqlconfig
from discord.ext import commands

class SampinfoCog(commands.Cog, name="SA-MP Server Info"):
    def __init__(self, bot):
        self.bot = bot

    async def UpdateSAMPInfo(self):
        while 1:
            try:
                sql = mysql.connector.connect(** mysqlconfig)
                cursor = sql.cursor()
                cursor.execute("SELECT SUM(Online) AS playercount FROM players WHERE Online = 1")
                data = cursor.fetchone()
                cursor.close()
                sql.close()

                game = discord.Game(f'RCRP ({data[0]}/150 players)')
                await self.bot.change_presence(activity = game)
            except:
                print("Error while updating player count.")

            await asyncio.sleep(1) #run every second

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(UpdateSAMPInfo(self))

def setup(bot):
    bot.add_cog(SampinfoCog(bot))