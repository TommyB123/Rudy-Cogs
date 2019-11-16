import discord
import aiomysql
from cogs.mysqlinfo import mysqlconfig
from discord.ext import commands

class OwnerCmdsCog(commands.Cog, name="Owner Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    @commands.is_owner()
    async def dms(self, ctx):
        await ctx.send("<https://imgur.com/a/yYK5dnZ>")

    @commands.command()
    @commands.is_owner()
    async def economy(self, ctx):
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT SUM(Bank) AS Bank, SUM(Check1) AS CheckSlot1, SUM(Check2) AS CheckSlot2, SUM(Check3) AS CheckSlot3 FROM players")
        playerdata = await cursor.fetchone()
        await cursor.execute("SELECT SUM(BankBalance) AS FBank FROM factions WHERE id != 3")
        factionbank = await cursor.fetchone()
        await cursor.execute("SELECT SUM(itemval) AS dollars FROM inventory WHERE item = 45 GROUP BY type ORDER BY type ASC")
        storedcash = await cursor.fetchall()
        cashsum = storedcash[0]['dollars'] + playerdata['Bank'] + playerdata['CheckSlot1'] + playerdata['CheckSlot2'] + playerdata['CheckSlot3'] + factionbank['FBank'] + storedcash[1]['dollars'] + storedcash[2]['dollars'] + storedcash[3]['dollars']
        await cursor.close()
        sql.close()

        embed = discord.Embed(title = 'RCRP Economy Statistics', color = 0xe74c3c, timestamp = ctx.message.created_at)
        embed.add_field(name = "In-Hand Cash", value = '${:,}'.format(storedcash[0]['dollars']))
        embed.add_field(name = "Player Banks", value = '${:,}'.format(playerdata['Bank']))
        embed.add_field(name = "Check Slot 1", value = '${:,}'.format(playerdata['CheckSlot1']))
        embed.add_field(name = "Check Slot 2", value = '${:,}'.format(playerdata['CheckSlot2']))
        embed.add_field(name = "Check Slot 3", value = '${:,}'.format(playerdata['CheckSlot3']))
        embed.add_field(name = 'Faction Banks (excluding ST)', value = '${:,}'.format(factionbank['FBank']))
        embed.add_field(name = 'Stored House Cash', value = '${:,}'.format(storedcash[1]['dollars']))
        embed.add_field(name = 'Stored Business Cash', value = '${:,}'.format(storedcash[2]['dollars']))
        embed.add_field(name = 'Stored Vehicle Cash', value = '${:,}'.format(storedcash[3]['dollars']))
        embed.add_field(name = 'Total', value = '${:,}'.format(cashsum))
        await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.is_owner()
    async def loadcog(self, ctx, *, cog:str):
        try:
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'Unable to load {cog}. Reason: {e}')
        else:
            await ctx.send(f'{cog} loaded successfully.')

    @commands.command(hidden = True)
    @commands.is_owner()
    async def unloadcog(self, ctx, *, cog:str):
        try:
            self.bot.unload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'Unable to unload {cog}. Reason: {e}')
        else:
            await ctx.send(f'{cog} unloaded successfully.')

    @commands.command(hidden = True)
    @commands.is_owner()
    async def reloadcog(self, ctx, *, cog:str):
        try:
            self.bot.reload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'Reloading of {cog} failed. Reason: {e}')
        else:
            await ctx.send(f'{cog} successfully reloaded.')

def setup(bot):
    bot.add_cog(OwnerCmdsCog(bot))