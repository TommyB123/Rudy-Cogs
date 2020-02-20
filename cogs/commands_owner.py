import discord
import aiomysql
from cogs.mysqlinfo import mysqlconfig
from discord.ext import commands

drugtypes = {
    47: "Low Grade Cocaine",
    48: "Medium Grade Cocaine",
    49: "High Grade Cocaine",
    51: "Low Grade Crack",
    52: "Medium Grade Crack",
    53: "High Grade Crack",
    55: "Marijuana",
    57: "Heroin"
}

class OwnerCmdsCog(commands.Cog, name="Owner Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Why I don't have my god damn DMs open")
    @commands.guild_only()
    @commands.is_owner()
    async def dms(self, ctx):
        await ctx.send("<https://imgur.com/a/yYK5dnZ>")

    @commands.command(help = "Collects statistics about the server's economy")
    @commands.guild_only()
    @commands.is_owner()
    async def economy(self, ctx):
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT SUM(Bank) AS Bank, SUM(Check1) AS CheckSlot1, SUM(Check2) AS CheckSlot2, SUM(Check3) AS CheckSlot3 FROM players")
        playerdata = await cursor.fetchone()
        await cursor.execute("SELECT SUM(BankBalance) AS FBank FROM factions WHERE id != 3")
        factionbank = await cursor.fetchone()
        await cursor.execute("SELECT SUM(itemval) AS dollars FROM inventory_player WHERE item = 45")
        inhandcash = await cursor.fetchone()
        await cursor.execute("SELECT SUM(itemval) AS dollars FROM inventory_house WHERE item = 45")
        housecash = await cursor.fetchone()
        await cursor.execute("SELECT SUM(itemval) AS dollars FROM inventory_bizz WHERE item = 45")
        bizzcash = await cursor.fetchone()
        await cursor.execute("SELECT SUM(itemval) AS dollars FROM inventory_vehicle WHERE item = 45")
        vehiclecash = await cursor.fetchone()
        cashsum = inhandcash['dollars'] + playerdata['Bank'] + playerdata['CheckSlot1'] + playerdata['CheckSlot2'] + playerdata['CheckSlot3'] + factionbank['FBank'] + housecash['dollars'] + bizzcash['dollars'] + vehiclecash['dollars']
        await cursor.close()
        sql.close()


        embed = discord.Embed(title = 'RCRP Economy Statistics', color = 0xe74c3c, timestamp = ctx.message.created_at)
        embed.add_field(name = "In-Hand Cash", value = '${:,}'.format(inhandcash['dollars']))
        embed.add_field(name = "Player Banks", value = '${:,}'.format(playerdata['Bank']))
        embed.add_field(name = "Check Slot 1", value = '${:,}'.format(playerdata['CheckSlot1']))
        embed.add_field(name = "Check Slot 2", value = '${:,}'.format(playerdata['CheckSlot2']))
        embed.add_field(name = "Check Slot 3", value = '${:,}'.format(playerdata['CheckSlot3']))
        embed.add_field(name = 'Faction Banks (excluding ST)', value = '${:,}'.format(factionbank['FBank']))
        embed.add_field(name = 'Stored House Cash', value = '${:,}'.format(housecash['dollars']))
        embed.add_field(name = 'Stored Business Cash', value = '${:,}'.format(bizzcash['dollars']))
        embed.add_field(name = 'Stored Vehicle Cash', value = '${:,}'.format(vehiclecash['dollars']))
        embed.add_field(name = 'Total', value = '${:,}'.format(cashsum))
        await ctx.send(embed = embed)
    
    @commands.command(help = "Collects statistics of drugs")
    @commands.guild_only()
    @commands.is_owner()
    async def drugs(self, ctx):
        drugs = {47:0, 48:0, 49:0, 51:0, 52:0, 53:0, 55:0, 57:0}
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT SUM(itemval) AS items, item FROM inventory_player WHERE item IN (47, 48, 49, 51, 52, 53, 55, 57) GROUP BY item")
        results = await cursor.fetchall()

        for drug in results:
            drugs[drug['item']] += drug['items']

        await cursor.execute("SELECT SUM(itemval) AS items, item FROM inventory_house WHERE item IN (47, 48, 49, 51, 52, 53, 55, 57) GROUP BY item")
        results = await cursor.fetchall()

        for drug in results:
            drugs[drug['item']] += drug['items']

        await cursor.execute("SELECT SUM(itemval) AS items, item FROM inventory_bizz WHERE item IN (47, 48, 49, 51, 52, 53, 55, 57) GROUP BY item")
        results = await cursor.fetchall()

        for drug in results:
            drugs[drug['item']] += drug['items']

        await cursor.execute("SELECT SUM(itemval) AS items, item FROM inventory_vehicle WHERE item IN (47, 48, 49, 51, 52, 53, 55, 57) GROUP BY item")
        results = await cursor.fetchall()

        for drug in results:
            drugs[drug['item']] += drug['items']

        embed = discord.Embed(title = 'RCRP Drug Statistics', color = 0xe74c3c, timestamp = ctx.message.created_at)
        embed.add_field(name = 'Low Grade Cocaine', value = '{:,}'.format(drugs[47]))
        embed.add_field(name = 'Medium Grade Cocaine', value = '{:,}'.format(drugs[48]))
        embed.add_field(name = 'High Grade Cocaine', value = '{:,}'.format(drugs[49]))
        embed.add_field(name = 'Low Grade Crack', value = '{:,}'.format(drugs[51]))
        embed.add_field(name = 'Medium Grade Crack', value = '{:,}'.format(drugs[52]))
        embed.add_field(name = 'High Grade Crack', value = '{:,}'.format(drugs[53]))
        embed.add_field(name = 'Marijuana', value = '{:,}'.format(drugs[55]))
        embed.add_field(name = 'Heroin', value = '{:,}'.format(drugs[57]))
        await ctx.send(embed = embed)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def roles(self, ctx):
        embed = discord.Embed(title = 'RCRP Discord Roles', color = 0xe74c3c, timestamp = ctx.message.created_at)
        for role in ctx.guild.roles:
            embed.add_field(name = role.name, value = role.id)
        await ctx.send(embed = embed)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def loadcog(self, ctx, *, cog:str):
        try:
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'Unable to load {cog}. Reason: {e}')
        else:
            await ctx.send(f'{cog} loaded successfully.')

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def unloadcog(self, ctx, *, cog:str):
        try:
            self.bot.unload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'Unable to unload {cog}. Reason: {e}')
        else:
            await ctx.send(f'{cog} unloaded successfully.')

    @commands.command()
    @commands.guild_only()
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