import discord
import aiomysql
from cogs.mysqlinfo import mysqlconfig
from cogs.utility import rcrp_utility
from discord.ext import commands

class PlayerCmdsCog(commands.Cog, name="Player Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    @commands.cooldown(1, 60)
    async def admins(self, ctx):
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT masters.Username AS mastername, players.Name AS charactername FROM masters JOIN players ON players.MasterAccount = masters.id WHERE AdminLevel != 0 AND Online = 1")

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("There are currently no admins in-game.")
            return

        embed = discord.Embed(title = 'In-game Administrators', color = 0xe74c3c, timestamp = ctx.message.created_at)

        results = await cursor.fetchall()
        for admininfo in results:
            embed.add_field(name = admininfo['mastername'], value = admininfo['charactername'], inline = True)

        await cursor.close()
        sql.close()
        await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.cooldown(1, 60)
    async def helpers(self, ctx):
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT masters.Username AS mastername, players.Name AS charactername FROM masters JOIN players ON players.MasterAccount = masters.id WHERE Helper != 0 AND Online = 1")

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("There are currently no helpers in-game.")
            return

        embed = discord.Embed(title = 'Ingame Helpers', color = 0xe74c3c, timestamp = ctx.message.created_at)

        results = await cursor.fetchall()
        for helperinfo in results:
            embed.add_field(name = helperinfo['mastername'], value = helperinfo['charactername'], inline = False)

        await cursor.close()
        sql.close()
        await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.cooldown(1, 60)
    async def players(self, ctx):
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT Name FROM players WHERE Online = 1 ORDER BY Name ASC")

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("There are currently no players in-game.")

        results = await cursor.fetchall()
        await cursor.close()
        sql.close()

        players = []
        for playerinfo in results:
            players.append(playerinfo[0])
        players = ','.join(players)
        players = players.replace(',', '\n')

        embed = discord.Embed(title = 'In-Game Players', color = 0xe74c3c, timestamp = ctx.message.created_at)
        embed.add_field(name = 'Online Players ({0})'.format(cursor.rowcount), value = players, inline = False)
        await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.cooldown(1, 60)
    async def factiononline(self, ctx):
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT COUNT(players.id) AS members, COUNT(IF(Online = 1, 1, NULL)) AS onlinemembers, factions.FactionName AS name FROM players JOIN factions ON players.Faction = factions.id WHERE Faction != 0 GROUP BY Faction ORDER BY Faction ASC")
        factiondata = await cursor.fetchall()
        await cursor.close()
        sql.close()

        embed = discord.Embed(title = "Faction List", color = 0xe74c3c, timestamp = ctx.message.created_at)
        for factioninfo in factiondata:
            embed.add_field(name = factioninfo['name'], value = '{0}/{1}'.format(factioninfo['onlinemembers'], factioninfo['members']), inline = False)
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(PlayerCmdsCog(bot))