import discord
import aiomysql
from redbot.core import commands, Config
from redbot.core.bot import Red

# roles
adminrole = 293441894585729024
managementrole = 310927289317588992
ownerrole = 293303836125298690

# guild ID for main RCRP guild
rcrpguildid = 93142223473905664

# all rcrp admin roles
staffroles = [ownerrole, adminrole, managementrole]


async def admin_check(ctx: commands.Context):
    if ctx.guild is not None and ctx.guild.id == rcrpguildid:
        for role in ctx.author.roles:
            if role.id in staffroles:
                return True
        return False
    else:
        return True


def rcrp_check(ctx: commands.Context):
    return (ctx.guild is not None and ctx.guild.id == rcrpguildid)


class RCRPFactions(commands.Cog, name="Faction Commands"):
    def __init__(self, bot: Red):
        default_guild = {
            "factionid": None
        }

        self.bot = bot
        self.config = Config.get_conf(self, 45599)
        self.config.register_guild(**default_guild)

    async def return_faction_name(self, factionid: int):
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT FactionName FROM factions WHERE id = %s", (factionid, ))

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            print(f"An invalid faction ID was passed to return_faction_name ({factionid})")
            return "Unknown"

        data = await cursor.fetchone()
        await cursor.close()
        sql.close()
        return data[0]

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if await self.config.guild(guild).factionid() is not None:
            await self.config.guild(guild).factionid.set(None)

    @commands.group()
    @commands.guild_only()
    async def faction(self, ctx: commands.Context):
        """Various faction-related commands"""
        pass

    @faction.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def factions(self, ctx: commands.Context):
        """Lists all of the current factions on the server"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()

        await cursor.execute("SELECT id, FactionName FROM factions ORDER BY id ASC")
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
        embed = discord.Embed(title='RCRP Factions', description=factionstring, color=0xe74c3c, timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)

    @faction.command()
    @commands.guild_only()
    @commands.is_owner()
    async def guilds(self, ctx: commands.Context):
        """Lists guild IDS associated with factions."""
        embed = discord.Embed(title='Linked Factions', color=0xe74c3c, timestamp=ctx.message.created_at)
        guilds = await self.config.all_guilds()
        for guild in guilds:
            factionid = guilds[guild]['factionid']
            factionname = await self.return_faction_name(factionid)
            embed.add_field(name=f'{factionname} ({factionid})', value=guild)
        await ctx.send(embed=embed)

    @faction.command()
    @commands.guild_only()
    @commands.is_owner()
    async def register(self, ctx: commands.Context, factionid: int):
        """Registers a Discord server as a faction Discord with the provided faction ID."""
        if await self.config.guild(ctx.guild).factionid() is not None:
            await ctx.send("This discord server is already linked to a faction.")
            return

        guilds = await self.config.all_guilds()
        for guild in guilds:
            if guilds[guild]['factionid'] == factionid:
                await ctx.send("This faction is already linked to another discord server.")
                return

        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
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
        factionname = await self.return_faction_name(factionid)
        await ctx.send(f'This discord server is now linked to {factionname}!')

    @faction.command()
    @commands.guild_only()
    @commands.is_owner()
    async def unregister(self, ctx: commands.Context):
        """Removes a Discord's faction association."""
        factionid = await self.config.guild(ctx.guild).factionid()
        if factionid is None:
            await ctx.send('This server is not linked to a faction.')
            return

        await self.config.guild(ctx.guild).factionid.set(None)
        factionname = await self.return_faction_name(factionid)
        await ctx.send(f'This server is no longer linked to {factionname}.')

    @faction.command()
    @commands.guild_only()
    async def members(self, ctx: commands.Context):
        """Lists all online members of a faction in verified, faction-specific discords"""
        factionid = await self.config.guild(ctx.guild).factionid()
        if factionid is None:
            await ctx.send('This command can only be used in verified, faction-specific Discord servers.')
            return

        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
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

        embed = discord.Embed(title=f'Online Members ({cursor.rowcount})', description=memberstring, color=0xe74c3c)
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)

        await cursor.close()
        sql.close()

    @faction.command()
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(rcrp_check)
    async def online(self, ctx: commands.Context):
        """Collects a list of factions and their online member counts"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT COUNT(players.id) AS members, COUNT(IF(Online = 1, 1, NULL)) AS onlinemembers, factions.FNameShort AS name FROM players JOIN factions ON players.Faction = factions.id WHERE Faction != 0 GROUP BY Faction ORDER BY Faction ASC")
        factiondata = await cursor.fetchall()
        await cursor.close()
        sql.close()

        embed = discord.Embed(title="Faction List", color=0xe74c3c, timestamp=ctx.message.created_at)
        for factioninfo in factiondata:
            embed.add_field(name=factioninfo['name'], value=f"{factioninfo['onlinemembers']}/{factioninfo['members']}", inline=True)
        await ctx.send(embed=embed)
