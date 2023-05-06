import discord
import aiomysql
from discord.ext import tasks
from redbot.core import commands
from redbot.core.bot import Red


class RCRPSampInfo(commands.Cog, name="SA-MP Server Info"):
    def __init__(self, bot: Red):
        self.bot = bot
        self.update_samp_info.add_exception_type(aiomysql.Error)
        self.update_samp_info.start()

    def cog_unload(self):
        self.update_samp_info.cancel()

    @tasks.loop(seconds=1)
    async def update_samp_info(self):
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT SUM(Online) AS playercount FROM players WHERE Online = 1")
        data = await cursor.fetchone()
        await cursor.close()
        sql.close()

        players = data[0]
        if players is None:
            players = 0

        game = discord.Game(f'RCRP - {players} {"players" if players != 1 else "player"}')
        await self.bot.change_presence(activity=game)

    @update_samp_info.before_loop
    async def before_update_samp_info(self):
        await self.bot.wait_until_ready()
