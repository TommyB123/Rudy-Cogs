import discord
import json
from utility import mysql_connect
from discord.ext import commands

factions = None
with open('files/factions.json', 'r') as file:
    factions = json.load(file)

async def ReturnFactionName(factionid: int):
    sql = await mysql_connect()
    cursor = await sql.cursor()
    await cursor.execute("SELECT FactionName FROM factions WHERE id = %s", (factionid, ))

    if cursor.rowcount == 0:
        await cursor.close()
        sql.close()
        print(f"An invalid faction ID was passed to ReturnFactionName ({factionid})")
        return "Unknown"
    
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()
    return data[0]

class FactionsCog(commands.Cog, name="Faction Commands"):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):            
        for faction in factions['factions']:
            if faction['discordid'] == guild.id:
                factions['factions'].pop(factions['factions'].index(faction))
                with open('files/factions.json', 'w') as file:
                    json.dump(factions, file)
                break
    
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
        if ctx.guild.id in [faction['discordid'] for faction in factions['factions']]:
            await ctx.send("This discord server is already linked to a faction.")
            return

        if factionid in [faction['factionid'] for faction in factions['factions']]:
            await ctx.send("This faction is already linked to another discord server.")
            return

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
        with open('files/factions.json', 'w') as file:
            json.dump(factions, file)
        factionname = await ReturnFactionName(factionid)
        await ctx.send(f'This discord server is now linked to {factionname}!')

    @commands.command(help = "Removes a discord server as a faction discord.")
    @commands.guild_only()
    @commands.is_owner()
    async def unregisterdiscord(self, ctx): 
        for faction in factions['factions']:
            if faction['discordid'] == ctx.guild.id:
                factionid = faction['factionid']
                factions['factions'].pop(factions['factions'].index(faction))
                with open('files/factions.json', 'w') as file:
                    json.dump(factions, file)
                factionname = await ReturnFactionName(factionid)
                await ctx.send(f'This server is no longer linked to {factionname}.')
                return

        await ctx.send('This server is not linked to a faction.')
    
    @commands.command(help = "Reloads faction data from the json file")
    @commands.guild_only()
    @commands.is_owner()
    async def reloadfactionjson(self, ctx):
        factions = None
        with open('files/factions.json', 'r') as file:
            factions = json.load(file)
        await ctx.send('Faction data file reloaded.')
    
    @commands.command(help = "Lists guild IDs associated with factions")
    @commands.guild_only()
    @commands.is_owner()
    async def factionguilds(self, ctx):
        embed = discord.Embed(title = 'Linked Factions', color = 0xe74c3c, timestamp = ctx.message.created_at)
        for faction in factions['factions']:
            factionid = faction['factionid']
            guildid = faction['discordid']
            factionname = await ReturnFactionName(factionid)
            embed.add_field(name = f'{factionname} ({factionid})', value = guildid)
        await ctx.send(embed = embed)

def setup(bot):
	bot.add_cog(FactionsCog(bot))
