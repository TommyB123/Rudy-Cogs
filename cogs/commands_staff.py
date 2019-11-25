import discord
import aiomysql
from cogs.utility import *
from discord.ext import commands
from cogs.mysqlinfo import mysqlconfig
from datetime import datetime

class StaffCmdsCog(commands.Cog, name="Staff Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Clear up to the last 10 messages")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def clear(self, ctx, *, amount : int = None):
        if amount == None or amount <= 0:
            await ctx.send("Usage: !clear [number of messages (1-10)]")
            return

        if amount > 10:
            await ctx.send("You cannot clear more than 10 messages at once.")
            return

        messages = await ctx.channel.history(limit = amount + 1).flatten()
        await ctx.channel.delete_messages(messages)

    @commands.command(help = "Clears all of the applications in the applications channel")
    @commands.guild_only()
    async def clearapps(self, ctx):
        if ctx.channel.id == 445668156824879123:
            messages = await ctx.channel.history().filter(rcrp_utility.appfilter).flatten()
            await ctx.channel.delete_messages(messages)

    @commands.command(help = "Fetches MA info of a verified discord member")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def whois(self, ctx, user: discord.User=None):
        if user == None:
            await ctx.send("Usage: !whois [discord user]")
            return

        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT id, Username, UNIX_TIMESTAMP(RegTimeStamp) AS RegStamp, LastLog FROM masters WHERE discordid = %s", (user.id, ))
        data = await cursor.fetchone()

        if cursor.rowcount == 0:
            await ctx.send(f"{user} does not have a Master Account linked to their Discord account.")
            await cursor.close()
            sql.close()
            return

        await cursor.close()
        sql.close()

        embed = discord.Embed(title = f"{data[1]} - {user}", url = f"https://redcountyrp.com/admin/masters/{data[0]}", color = 0xe74c3c)
        embed.add_field(name = "Account ID", value = data[0], inline = False)
        embed.add_field(name = "Username", value = data[1], inline = False)
        embed.add_field(name = "Registration Date", value = datetime.utcfromtimestamp(data[2]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        embed.add_field(name = "Last Login Date", value = datetime.utcfromtimestamp(data[3]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        await ctx.send(embed = embed)

    @commands.command(help = "Fetches the discord account of a member based on their MA name")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def find(self, ctx, name : str = None):
        if name == None:
            await ctx.send("Usage: !find [Master Account Name]")
            return

        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT id, discordid, UNIX_TIMESTAMP(RegTimeStamp) AS RegStamp, LastLog FROM masters WHERE Username = %s", (name, ))

        if cursor.rowcount == 0:
            await ctx.send(f"{name} is not a valid account name.")
            await cursor.close()
            sql.close()
            return

        data = await cursor.fetchone()
        await cursor.close()
        sql.close()

        if data[1] == None:
            await ctx.send(f"{name} does not have a Discord account linked to their MA.")
            return

        matcheduser = await self.bot.fetch_user(data[1])
        embed = discord.Embed(title = f"{name}", url = f"https://redcountyrp.com/admin/masters/{data[0]}", color = 0xe74c3c)
        embed.add_field(name = "Discord User", value = matcheduser.mention)
        embed.add_field(name = "Account ID", value = data[0], inline = False)
        embed.add_field(name = "Username", value = name, inline = False)
        embed.add_field(name = "Registration Date", value = datetime.utcfromtimestamp(data[2]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        embed.add_field(name = "Last Login Date", value = datetime.utcfromtimestamp(data[3]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        await ctx.send(embed = embed)

    @commands.command(help = "Bans a member from the RCRP discord")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def ban(self, ctx, user: discord.User = None, *, banreason):
        if not user:
            await ctx.send("Invalid user.")
            return

        if len(banreason) == 0:
            await ctx.send("Enter a reason.")
            return

        bannedmember = ctx.guild.get_member(user.id)
        if rcrp_utility.isadmin(bannedmember):
            await ctx.send("You can't ban other staff idiot boy.")
            return

        try:
            adminuser = await self.bot.fetch_user(ctx.author.id)
            embed = discord.Embed(title = 'Banned', description = f'You have been banned from the Red County Roleplay Discord server by {adminuser.name}', color = 0xe74c3c, timestamp = ctx.message.created_at)
            embed.add_field(name = 'Ban Reason', value = banreason)
            await user.send(embed = embed)
        except:
            print("couldn't ban user because dms off")

        baninfo = f"{banreason} - Banned by {adminuser.name}"
        await ctx.guild.ban(bannedmember, reason = baninfo, delete_message_days = 0)
        await ctx.send(f"{bannedmember.mention} has been successfully banned.")

    @commands.command(help = "Unbans a member from the RCRP discord")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def unban(self, ctx, target):
        banned_user = await self.bot.fetch_user(target)
        if not banned_user:
            await ctx.send("Invalid user. Enter their discord ID, nothing else.")
            return

        bans = await ctx.guild.bans()
        for ban in bans:
            if ban.user.id == banned_user.id:
                await ctx.guild.unban(ban.user)
                await ctx.send(f"{ban.user.mention} has been successfully unbanned")
                return

        await ctx.send("Could not find any bans for that user.")

    @commands.command(help = "Searches all existing bans for a banned user.")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def baninfo(self, ctx, target: str = ""):
        banned_user = await self.bot.fetch_user(target)
        if not banned_user:
            await ctx.send("Invalid user.")
            return

        bans = await ctx.guild.bans()
        for ban in bans:
            if ban.user.id == banned_user.id:
                await ctx.send(f"{ban.user.mention} was banned for the following reason: {ban.reason}")
                return
        await ctx.send("Could not find any ban info for that user.")

    @commands.command(help = "Mutes a member")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def mute(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Invalid user.")
            return

        if rcrp_utility.isadmin(member):
            await ctx.send("You can't mute other staff.")
            return

        if rcrp_utility.ismuted(member):
            await ctx.send(f"{member.mention} is already muted.")
            return

        await member.add_roles(ctx.guild.get_role(mutedrole))
        await ctx.send(f"{member.mention} has been muted.")

    @commands.command(help = "Unmutes a member")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def unmute(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Invalid user.")
            return

        if rcrp_utility.isadmin(member):
            await ctx.send("You can't mute other staff.")
            return

        if not rcrp_utility.ismuted(member):
            await ctx.send(f"{member.mention} is not muted.")
            return

        await member.remove_roles(ctx.guild.get_role(mutedrole))
        await ctx.send(f"{member.mention} has been unmuted.")

    @commands.command(help = "Sends a message as Rudy")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_management)
    async def speak(self, ctx, *, copymessage:str):
        if len(copymessage) == 0:
            return

        await ctx.message.delete()
        await ctx.send(copymessage)

    @commands.command(help = "Fetches the information of a user specified house")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def house(self, ctx, *, address:str = None):
        if address is None:
            await ctx.send("Usage: !house [house address]")
            return

        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT houses.id, OwnerSQLID, Description, players.Name AS OwnerName, InsideID, ExteriorFurnLimit, Price FROM houses LEFT JOIN players ON players.id = houses.OwnerSQLID WHERE Description = %s", (address, ))

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("Invalid house address.")
            return

        house = await cursor.fetchone()
        await cursor.close()
        sql.close()

        if house['OwnerName'] is None:
            if house['OwnerSQLID'] == -5:
                house['OwnerName'] = "Silver Trading"
            else:
                house['OwnerName'] = "Unowned"

        embed = discord.Embed(title = house['Description'], color = 0xe74c3c)
        embed.set_thumbnail(url = f"https://redcountyrp.com/images/houses/{house['id']}.png")
        embed.add_field(name = "ID", value = house['id'], inline = False)
        embed.add_field(name = "Owner", value = house['OwnerName'], inline = False)
        embed.add_field(name = "Price", value = '${:,}'.format(house['Price']), inline = False)
        embed.add_field(name = "Interior", value = house['InsideID'], inline = False)
        embed.add_field(name = "Ext Furn Limit", value = house['ExteriorFurnLimit'], inline = False)
        await ctx.send(embed = embed)

    @commands.command(help = "Fetches the information of a user specified business")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def business(self, ctx, *, description:str = None):
        if description is None:
            await ctx.send("Usage: !business [business name]")
            return

        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT bizz.id, OwnerSQLID, Description, players.Name AS OwnerName, Price, BizzEarnings, IsSpecial, Loaned FROM bizz LEFT JOIN players ON players.id = bizz.OwnerSQLID WHERE Description = %s", (description, ))

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("Invalid business.")
            return

        bizz = await cursor.fetchone()
        await cursor.close()
        sql.close()

        if bizz['OwnerName'] is None:
            if bizz['OwnerSQLID'] == -5:
                bizz['OwnerName'] = "Silver Trading"
            else:
                bizz['OwnerName'] = "Unowned"

        embed = discord.Embed(title = bizz['Description'], color = 0xe74c3c)
        embed.set_thumbnail(url = f"https://redcountyrp.com/images/businesses/{bizz['id']}.png")
        embed.add_field(name = "ID", value = bizz['id'], inline = False)
        embed.add_field(name = "Owner", value = bizz['OwnerName'], inline = False)
        embed.add_field(name = "Price", value = '${:,}'.format(bizz['Price']), inline = False)
        embed.add_field(name = "Earnings", value = '${:,}'.format(bizz['BizzEarnings']), inline = False)
        embed.add_field(name = "Special Int", value = 'Yes' if bizz['IsSpecial'] == 1 else 'No', inline = False)
        embed.add_field(name = "Loaned", value = 'Yes' if bizz['Loaned'] == 1 else 'No', inline = False)
        await ctx.send(embed = embed)

    @commands.command(help = "Get the URL of a discord user's avatar")
    @commands.guild_only()
    @commands.check(rcrp_utility.is_admin)
    async def avatar(self, ctx, member:discord.Member = None):
        if member is None:
            await ctx.send("Usage: /avatarurl [member]")
            return

        await ctx.send(f'Avatar of {member.mention}: {member.avatar_url}')


def setup(bot):
    bot.add_cog(StaffCmdsCog(bot))