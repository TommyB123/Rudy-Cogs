import discord
import aiomysql
from redbot.core import commands
from .config import mysqlconfig
from .utility import rcrp_check, admin_check

class RCRPCommands(commands.Cog):
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def admins(self, ctx: commands.Context):
        """Sends a list of in-game administrators"""
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT masters.Username AS mastername, players.Name AS charactername FROM masters JOIN players ON players.MasterAccount = masters.id WHERE AdminLevel != 0 AND Online = 1")

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("There are currently no admins in-game.")
            return

        results = await cursor.fetchall()
        embed = discord.Embed(title = 'In-game Administrators', color = 0xe74c3c, timestamp = ctx.message.created_at)
        for admininfo in results:
            embed.add_field(name = admininfo['mastername'], value = admininfo['charactername'], inline = True)

        await cursor.close()
        sql.close()
        await ctx.send(embed = embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(rcrp_check)
    async def helpers(self, ctx: commands.Context):
        """Sends a list of in-game helpers"""
        sql = await aiomysql.connect(**mysqlconfig)
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
            embed.add_field(name = helperinfo['mastername'], value = helperinfo['charactername'])

        await cursor.close()
        sql.close()
        await ctx.send(embed = embed)

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    async def player(self, ctx: commands.Context, *, playername: str):
        """Queries the SA-MP server to see if a player with the specified name is in-game"""
        playername = playername.replace(' ', '_')
        playername = discord.utils.escape_mentions(playername)
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT NULL FROM players WHERE Name = %s AND Online = 1", (playername, ))

        if cursor.rowcount == 0: #player is not in-game
            await ctx.send(f'{playername} is not currently in-game.')
        else:
            await ctx.send(f'{playername} is currently in-game.')

    @commands.command()
    @commands.guild_only()
    async def gta(self, ctx: commands.Context):
        """Sends two links providing clean copies of GTA SA. Useful for when modded games break and etc""" 
        await ctx.send("https://tommyb.ovh/files/cleangtasa.7z - Full game (3.6 GB)\nhttps://tommyb.ovh/files/cleangtasa-small.7z - Compressed/Removed audio (600MB)\n\nhttps://rc-rp.com/03dl - SA-MP 0.3.DL")

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    async def mipmapped(self, ctx: commands.Context):
        """Sends a link with the GTA SA mipmapped mod"""
        await ctx.send("https://tommyb.ovh/files/GTA-SA-Fully-Mipmapped.7z")
