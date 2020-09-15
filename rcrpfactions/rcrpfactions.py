import discord
import json
from .utility import mysql_connect, admin_check, rcrp_check
from redbot.core import commands, Config

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

class RCRPFactions(commands.Cog, name="Faction Commands"):
    def __init__(self, bot: discord.Client):
        default_guild = {
            "factionid": None
        }
        
        self.bot = bot
        self.config = Config.get_conf(self, 45599)
        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if await self.config.guild(guild).factionid() != None:
            await self.config.guild(guild).factionid.set(None)
    
    @commands.group()
    @commands.guild_only()
    async def faction(self, ctx):
        """Various faction-related commands"""
        pass

    @faction.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def factions(self, ctx):
        """Lists all of the current factions on the server"""
        sql = await mysql_connect()
        cursor = await sql.cursor()

        await cursor.execute("SELECT id, FactionName FROM factions ORDER BY id ASC", ())
        if cursor.rowcount == 0:
            await ctx.send("There are apparently no factions currently.")
            await cursor.close()
            sql.close()
            return
        
        data = await cursor.fetchall()
        await cursor.close()
        sql.close()

        factionstring = []
        for faction in data:
            factionstring.append(f'{faction[1]} (ID {faction[0]})')
        factionstring = '\n'.join(factionstring)
        embed = discord.Embed(title = 'RCRP Factions', description = factionstring, color = 0xe74c3c, timestamp = ctx.message.created_at)
        await ctx.send(embed = embed)
    
    @faction.command(help = "Lists guild IDs associated with factions")
    @commands.guild_only()
    @commands.is_owner()
    async def guilds(self, ctx):
        embed = discord.Embed(title = 'Linked Factions', color = 0xe74c3c, timestamp = ctx.message.created_at)
        guilds = await self.config.all_guilds()
        for guild in guilds:
            factionid = guilds[guild]['factionid']
            factionname = await ReturnFactionName(factionid)
            embed.add_field(name = f'{factionname} ({factionid})', value = guild)
        await ctx.send(embed = embed)
    
    @faction.command()
    @commands.guild_only()
    @commands.is_owner()
    async def register(self, ctx, factionid: int):
        """Registers a Discord server as a faction Discord with the provided faction ID."""
        if await self.config.guild(ctx.guild).factionid() != None:
            await ctx.send("This discord server is already linked to a faction.")
            return

        guilds = await self.config.all_guilds()
        for guild in guilds:
            if guilds[guild]['factionid'] == factionid:
                await ctx.send("This faction is already linked to another discord server.")
                return

        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("SELECT NULL FROM factions WHERE id = %s", (factionid, ))

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send('Invalid faction ID.')
            return

        await cursor.close()
        sql.close()

        await self.config.guild(ctx.guild).factionid.set(factionid)
        factionname = await ReturnFactionName(factionid)
        await ctx.send(f'This discord server is now linked to {factionname}!')

    @faction.command()
    @commands.guild_only()
    @commands.is_owner()
    async def unregister(self, ctx):
        """Removes a Discord's faction association."""
        factionid = await self.config.guild(ctx.guild).factionid()
        if factionid == None:
            await ctx.send('This server is not linked to a faction.')
            return
        
        await self.config.guild(ctx.guild).factionid.set(None)
        factionname = await ReturnFactionName(factionid)
        await ctx.send(f'This server is no longer linked to {factionname}.')

    @faction.command()
    @commands.guild_only()
    async def members(self, ctx):
        """Lists all online members of a faction in verified, faction-specific discords"""
        factionid = await self.config.guild(ctx.guild).factionid()
        if factionid == None:
            await ctx.send('This command can only be used in verified, faction-specific Discord servers.')
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
