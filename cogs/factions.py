import discord
import json
from utility import mysql_connect
from discord.ext import commands

factions = None
with open('files/factions.json', 'r') as file:
    factions = json.load(file)

def UpdateFactionJSON():
    with open('files/factions.json', 'w') as file:
        json.dump(factions, file)

class FactionsCog(commands.Cog, name="Faction Commands"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(help = "Lists all online members of a faction in verified, faction-specific discords")
    @commands.guild_only()
    async def members(self, ctx):
        factionid = None
        for faction in factions['factions']:
            if faction['discordid'] == ctx.guild.id:
                factionid = faction['factionid']
                break

        if factionid == None:
            await ctx.send('This command can only be used in verified, faction-specific discord servers.')
            return

        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("SELECT Name, factionranks.rankname, masters.Username FROM players LEFT JOIN factionranks ON players.Faction = factionranks.fid LEFT JOIN masters ON masters.id = players.MasterAccount WHERE Faction = %s AND factionranks.slot = FactionRank AND Online = 1 ORDER BY FactionRank DESC", (factionid, ))

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send('There are currently no members online.')
            return
        
        members = await cursor.fetchall()
        memberstring = []
        for member in members:
            memberstring.append(f'{member[1]} {member[0]} ({member[2]})')
        memberstring = '\n'.join(memberstring)
        memberstring = memberstring.replace('_', ' ')

        embed = discord.Embed(title = f'Online Members ({cursor.rowcount})', description = memberstring, color = 0xe74c3c, timestamp = ctx.message.created_at)
        await ctx.send(embed = embed)

        await cursor.close()
        sql.close()
    
    @commands.command(help = "Registers a discord server as a faction discord with the provided faction ID.")
    @commands.guild_only()
    @commands.is_owner()
    async def registerdiscord(self, ctx, factionid: int):
        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("SELECT NULL FROM factions WHERE id = %s", (factionid, ))

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send('Invalid faction ID.')

        await cursor.close()
        sql.close()

        factions['factions'].append(dict(discordid = ctx.guild.id, factionid = factionid))
        await ctx.send(f'This discord server is now linked to faction {factionid}!')
        UpdateFactionJSON()

    @commands.command(help = "Removes a discord server as a faction discord.")
    @commands.guild_only()
    @commands.is_owner()
    async def removediscord(self, ctx): 
        for i in range(len(factions['factions'])):
            if factions['factions'][i]['discordid'] == ctx.guild.id:
                del factions['factions'][i]
                UpdateFactionJSON()
                await ctx.send('This server is no longer linked to a faction.')
                return

        await ctx.send('This server is not linked to a faction.')

def setup(bot):
	bot.add_cog(FactionsCog(bot))
