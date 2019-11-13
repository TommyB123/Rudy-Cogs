import discord
import utility
import mysqlinfo
import mysql.connector

from discord import commands

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
            await ctx.send("There are currently no admins ingame.")
            return

        embed = discord.Embed(title = 'Ingame Administrators', color = 0xe74c3c, timestamp = ctx.message.created_at)

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
            await ctx.send("There are currently no helpers ingame.")
            return

        embed = discord.Embed(title = 'Ingame Helpers', color = 0xe74c3c, timestamp = ctx.message.created_at)

        for helperinfo in cursor:
            embed.add_field(name = helperinfo['mastername'], value = helperinfo['charactername'], inline = False)

        cursor.close()
        sql.close()
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(PlayerCmdsCog(bot))