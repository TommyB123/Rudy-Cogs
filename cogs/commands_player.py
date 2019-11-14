import discord
import mysql.connector
from cogs.mysqlinfo import mysqlconfig
from cogs.utility import rcrp_utility
from discord.ext import commands

class PlayerCmdsCog(commands.Cog, name="Player Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    @commands.cooldown(1, 60)
    async def admins(self, ctx):
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor(buffered = True, dictionary = True)
        cursor.execute("SELECT masters.Username AS mastername, players.Name AS charactername FROM masters JOIN players ON players.MasterAccount = masters.id WHERE AdminLevel != 0 AND Online = 1")

        if cursor.rowcount == 0:
            cursor.close()
            sql.close()
            await ctx.send("There are currently no admins in-game.")
            return

        embed = discord.Embed(title = 'In-game Administrators', color = 0xe74c3c, timestamp = ctx.message.created_at)

        for admininfo in cursor:
            embed.add_field(name = admininfo['mastername'], value = admininfo['charactername'], inline = True)

        cursor.close()
        sql.close()
        await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.cooldown(1, 60)
    async def helpers(self, ctx):
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor(buffered = True, dictionary = True)
        cursor.execute("SELECT masters.Username AS mastername, players.Name AS charactername FROM masters JOIN players ON players.MasterAccount = masters.id WHERE Helper != 0 AND Online = 1")

        if cursor.rowcount == 0:
            cursor.close()
            sql.close()
            await ctx.send("There are currently no helpers in-game.")
            return

        embed = discord.Embed(title = 'Ingame Helpers', color = 0xe74c3c, timestamp = ctx.message.created_at)

        for helperinfo in cursor:
            embed.add_field(name = helperinfo['mastername'], value = helperinfo['charactername'], inline = False)

        cursor.close()
        sql.close()
        await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.cooldown(1, 60)
    async def players(self, ctx):
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("SELECT Name FROM players WHERE Online = 1 ORDER BY Name ASC")

        if cursor.rowcount == 0:
            cursor.close()
            sql.close()
            await ctx.send("There are currently no players in-game.")

        embed = discord.Embed(title = 'In-Game Players', color = 0xe74c3c, timestamp = ctx.message.created_at)

        players = []
        for playerinfo in cursor:
            players.append(playerinfo[0])

        players = ','.join(players)
        players = players.replace(',', '\n')
        embed.add_field(name = 'Online Players ({0})'.format(cursor.rowcount), value = players, inline = False)

        cursor.close()
        sql.close()
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(PlayerCmdsCog(bot))