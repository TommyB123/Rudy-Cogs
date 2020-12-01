import discord
import aiomysql
import json
from redbot.core import commands
from .config import mysqlconfig

#rcrp guild ID
rcrpguildid = 93142223473905664

#roles
adminrole = 293441894585729024
managementrole = 310927289317588992
ownerrole = 293303836125298690
staffroles = [ownerrole, adminrole, managementrole]

async def rcrp_check(ctx: commands.Context):
    return (ctx.guild.id == rcrpguildid)

async def admin_check(ctx: commands.Context):
    if ctx.guild.id == rcrpguildid:
        for role in ctx.author.roles:
            if role.id in staffroles:
                return True
        return False
    else:
        return True

class RCRPCommands(commands.Cog):
    def __init__(self):
        self.relay_channel_id = 776943930603470868

    async def send_relay_channel_message(self, ctx: commands.Context, message: str):
        relaychannel = ctx.guild.get_channel(self.relay_channel_id)
        await relaychannel.send(message)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(rcrp_check)
    async def admins(self, ctx: commands.Context):
        """Sends a list of in-game administrators"""
        rcrp_message = {
            "callback": "FetchAdminListForDiscord",
            "channel": str(ctx.channel.id)
        }

        final = json.dumps(rcrp_message)
        self.send_relay_channel_message(ctx, final)

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
    async def vehicleinfo(self, ctx: commands.Context, vehicle: str):
        """Fetches all information related to a vehicle model from the SA-MP server"""
        rcrp_message = {
            "callback": "FetchVehicleInfoForDiscord",
            "vehicle": vehicle,
            "channel": str(ctx.channel.id)
        }

        message = json.dumps(rcrp_message)
        await self.send_relay_channel_message(ctx, message)

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
