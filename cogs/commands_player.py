import discord
import aiomysql
from cogs.mysqlinfo import mysqlconfig
from cogs.utility import *
from discord.ext import commands

class PlayerCmdsCog(commands.Cog, name="Player"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Collects a list of in-game administrators (60 sec cooldown)")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(rcrp_check)
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

    @commands.command(help = "Collects a list of in-game helpers (60 sec cooldown)")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(rcrp_check)
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

    @commands.command(help = "Lists all in-game players (60 sec cooldown)")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(rcrp_check)
    async def players(self, ctx):
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT SUM(Online) FROM players WHERE Online = 1")

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("There are currently no players in-game.")

        results = await cursor.fetchone()
        await cursor.close()
        sql.close()

        players = results[0]
        if players == None:
            players = 0

        embed = discord.Embed(title = f'In-Game Players - {players}', description = 'To see if a particular player is in-game, use !player', color = 0xe74c3c, timestamp = ctx.message.created_at)
        await ctx.send(embed = embed)

    @commands.command(help = "See if a character is in-game")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(rcrp_check)
    async def player(self, ctx, *, playername:str = None):
        if playername is None:
            await ctx.send("Usage: !player [full character name]")
            return
    
        playername = playername.replace(' ', '_')
        playername = discord.utils.escape_mentions(playername)
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT NULL FROM players WHERE Name = %s AND Online = 1", (playername, ))

        if cursor.rowcount == 0: #player is not in-game
            await ctx.send(f'{playername} is not currently in-game.')
        else:
            await ctx.send(f'{playername} is currently in-game.')

    @commands.command(help = "Lists all official factions and their member counts")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(rcrp_check)
    async def factiononline(self, ctx):
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT COUNT(players.id) AS members, COUNT(IF(Online = 1, 1, NULL)) AS onlinemembers, factions.FNameShort AS name FROM players JOIN factions ON players.Faction = factions.id WHERE Faction != 0 GROUP BY Faction ORDER BY Faction ASC")
        factiondata = await cursor.fetchall()
        await cursor.close()
        sql.close()

        embed = discord.Embed(title = "Faction List", color = 0xe74c3c, timestamp = ctx.message.created_at)
        for factioninfo in factiondata:
            embed.add_field(name = factioninfo['name'], value = '{0}/{1}'.format(factioninfo['onlinemembers'], factioninfo['members']), inline = True)
        await ctx.send(embed = embed)

    @commands.command(help = "piracy")
    @commands.guild_only()
    @commands.check(rcrp_check)
    async def gta(self, ctx):
        await ctx.send("https://tommyb.ovh/files/cleangtasa.7z - Full game (3.6 GB)\nhttps://tommyb.ovh/files/cleangtasa-small.7z - Compressed/Removed audio (600MB)\n\nhttps://rc-rp.com/03dl - SA-MP 0.3.DL")

    @commands.command(help = "GTA SA fully mipmapped link")
    @commands.guild_only()
    @commands.check(rcrp_check)
    async def mipmapped(self, ctx):
        await ctx.send("https://tommyb.ovh/files/GTA-SA-Fully-Mipmapped.7z")

def setup(bot):
    bot.add_cog(PlayerCmdsCog(bot))