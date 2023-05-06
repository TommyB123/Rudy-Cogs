import discord
import aiomysql
import json
from redbot.core import commands
from redbot.core.utils import menus
from redbot.core.bot import Red

# rcrp guild ID
rcrpguildid = 93142223473905664

# roles
adminrole = 293441894585729024
managementrole = 310927289317588992
ownerrole = 293303836125298690
staffroles = [ownerrole, adminrole, managementrole]


async def admin_check(ctx: commands.Context):
    if ctx.guild is not None and ctx.guild.id == rcrpguildid:
        for role in ctx.author.roles:
            if role.id in staffroles:
                return True
        return False
    else:
        return True


class RCRPCommands(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.relay_channel_id = 776943930603470868

    async def send_relay_channel_message(self, ctx: commands.Context, message: str):
        relaychannel = ctx.guild.get_channel(self.relay_channel_id)
        await relaychannel.send(message)

    @commands.command()
    @commands.guild_only()
    async def players(self, ctx: commands.Context):
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT Name FROM players WHERE Online = 1 ORDER BY Name ASC")
        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send('There are currently no players in-game.')
            return

        totalcount = 0
        counter = 0
        embeds = []
        string = ""
        players = await cursor.fetchall()
        for player in players:
            string += f'{player[0]}\n'
            counter += 1
            totalcount += 1
            if counter == 25 or totalcount == cursor.rowcount:
                embed = discord.Embed(title=f'Online Players - {cursor.rowcount}', description=string, color=0xe74c3c, timestamp=ctx.message.created_at)
                embed.set_footer(text='Use the !player command to view if a specific player is online.', icon_url=self.bot.user.avatar_url)
                embeds.append(embed)
                string = ""
                counter = 0

        message: discord.Message = await ctx.send(embed=discord.Embed(description='Formatting the player list. Please wait.'))
        menus.start_adding_reactions(message, menus.DEFAULT_CONTROLS)
        await menus.menu(ctx, embeds, menus.DEFAULT_CONTROLS, message)

        # try to delete the message after the timeout in the event that the user didn't close the menu
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 60)
    async def admins(self, ctx: commands.Context):
        """Sends a list of in-game administrators"""
        rcrp_message = {
            "callback": "FetchAdminListForDiscord",
            "channel": str(ctx.channel.id)
        }

        final = json.dumps(rcrp_message)
        await self.send_relay_channel_message(ctx, final)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 60)
    async def helpers(self, ctx: commands.Context):
        """Sends a list of in-game helpers"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT masters.Username AS mastername, players.Name AS charactername FROM masters JOIN players ON players.MasterAccount = masters.id WHERE Helper != 0 AND Online = 1")

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("There are currently no helpers in-game.")
            return

        results = await cursor.fetchall()
        embed = discord.Embed(title='Ingame Helpers', color=0xe74c3c, timestamp=ctx.message.created_at)
        for helperinfo in results:
            embed.add_field(name=helperinfo['mastername'], value=helperinfo['charactername'])

        await cursor.close()
        sql.close()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def player(self, ctx: commands.Context, *, playername: str):
        """Queries the SA-MP server to see if a player with the specified name is in-game"""
        playername = playername.replace(' ', '_')
        playername = discord.utils.escape_mentions(playername)
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT NULL FROM players WHERE Name = %s AND Online = 1", (playername, ))

        if cursor.rowcount == 0:  # player is not in-game
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
