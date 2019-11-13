import discord
import utility
import mysqlinfo
import mysql.connector

from discord import commands

class StaffCmdsCog(commands.Cog, name="Staff Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    @commands.check(is_admin)
    async def clear(self, ctx, *, amount : int = 0):
        if amount == 0:
            return

        if amount > 10:
            await ctx.send("You cannot clear more than 10 messages at once.")
            return

        messages = await ctx.channel.history(limit = amount + 1).flatten()
        await ctx.channel.delete_messages(messages)

    @commands.command(hidden = True)
    async def clearapps(ctx):
        if ctx.channel.id == 445668156824879123:
            messages = await ctx.channel.history().filter(predicate).flatten()
            await ctx.channel.delete_messages(messages)

    @commands.command(hidden = True)
    @commands.check(is_admin)
    async def whois(self, ctx, user: discord.User=None):
        if not user:
            await ctx.send("Invalid user.")
            return

        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("SELECT id, Username, UNIX_TIMESTAMP(RegTimeStamp) AS RegStamp, LastLog FROM masters WHERE discordid = %s", (user.id, ))
        data = cursor.fetchone()

        if cursor.rowcount == 0:
            await ctx.send("{user} does not have a Master Account linked to their Discord account.")
            cursor.close()
            sql.close()
            return

        cursor.close()
        sql.close()

        embed = discord.Embed(title = "{data[1]} - {user}", url = "https://redcountyrp.com/admin/masters/{data[0]}", color = 0xe74c3c)
        embed.add_field(name = "Account ID", value = data[0], inline = False)
        embed.add_field(name = "Username", value = data[1], inline = False)
        embed.add_field(name = "Registration Date", value = datetime.utcfromtimestamp(data[2]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        embed.add_field(name = "Last Login Date", value = datetime.utcfromtimestamp(data[3]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.check(is_admin)
    async def find(self, ctx, name : str = 'None'):
        if name == 'None':
            return

        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor(buffered = True)
        cursor.execute("SELECT id, discordid, UNIX_TIMESTAMP(RegTimeStamp) AS RegStamp, LastLog FROM masters WHERE Username = %s", (name, ))

        if cursor.rowcount == 0:
            await ctx.send("{name} is not a valid account name.")
            cursor.close()
            sql.close()
            return

        data = cursor.fetchone()
        cursor.close()
        sql.close()

        if data[1] == None:
            await ctx.send("{name} does not have a Discord account linked to their MA.")
            return

        matcheduser = await self.bot.fetch_user(data[1])
        embed = discord.Embed(title = "{name}", url = "https://redcountyrp.com/admin/masters/{data[0]}", color = 0xe74c3c)
        embed.add_field(name = "Discord User", value = matcheduser.id.mention)
        embed.add_field(name = "Account ID", value = data[0], inline = False)
        embed.add_field(name = "Username", value = name, inline = False)
        embed.add_field(name = "Registration Date", value = datetime.utcfromtimestamp(data[2]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        embed.add_field(name = "Last Login Date", value = datetime.utcfromtimestamp(data[3]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.check(is_admin)
    async def ban(self, ctx, user: discord.User = None, *, banreason):
        if not user:
            await ctx.send("Invalid user.")
            return

        if len(banreason) == 0:
            await ctx.send("Enter a reason.")
            return

        bannedmember = ctx.guild.get_member(user.id)
        if isadmin(bannedmember):
            await ctx.send("You can't ban other staff idiot boy.")
            return

        try:
            adminuser = await self.bot.fetch_user(ctx.author.id)
            embed = discord.Embed(title = 'Banned', description = 'You have been banned from the Red County Roleplay Discord server by {adminuser.name}', color = 0xe74c3c, timestamp = ctx.message.created_at)
            embed.add_field(name = 'Ban Reason', value = banreason)
            await user.send(embed = embed)
        except:
            print("couldn't ban user because dms off")

        baninfo = "{banreason} - Banned by {adminuser.name}"
        await ctx.guild.ban(bannedmember, reason = baninfo, delete_message_days = 0)
        await ctx.send("{bannedmember.id.mention} has been successfully banned.")

    @commands.command(hidden = True)
    @commands.check(is_admin)
    async def unban(self, ctx, target):
        banned_user = await self.bot.fetch_user(target)
        if not banned_user:
            await ctx.send("Invalid user. Enter their discord ID, nothing else.")
            return

        bans = await ctx.guild.bans()
        for ban in bans:
            if ban.user.id == banned_user.id:
                await ctx.guild.unban(ban.user)
                await ctx.send("{ban.user.mention} has been successfully unbanned")
                return

        await ctx.send("Could not find any bans for that user.")

    @commands.command(hidden = True)
    @commands.check(is_admin)
    async def baninfo(self, ctx, target: str = ""):
        banned_user = await self.bot.fetch_user(target)
        if not banned_user:
            await ctx.send("Invalid user.")
            return

        bans = await ctx.guild.bans()
        for ban in bans:
            if ban.user.id == banned_user.id:
                await ctx.send("{ban.user.mention} was banned for the following reason: {ban.reason}")
                return
        await ctx.send("Could not find any ban info for that user.")

    @commands.command(hidden = True)
    @commands.check(is_admin)
    async def mute(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Invalid user.")
            return

        if isadmin(member):
            await ctx.send("You can't mute other staff.")
            return

        if ismuted(member):
            await ctx.send("{member.id.mention} is already muted.")
            return

        await member.add_roles(ctx.guild.get_role(mutedrole))
        await ctx.send("{member.id.mention} has been muted.")

    @commands.command(hidden = True)
    @commands.check(is_admin)
    async def unmute(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Invalid user.")
            return

        if isadmin(member):
            await ctx.send("You can't mute other staff.")
            return

        if not ismuted(member):
            await ctx.send("{member.id.mention} is not muted.")
            return

        await member.remove_roles(ctx.guild.get_role(mutedrole))
        await ctx.send("{member.id.mention} has been unmuted.")

    @commands.command(hidden = True)
    @commands.check(is_management)
    async def verify(self, ctx, member: discord.Member = None, masteraccount: str = " "):
        if not member:
            await ctx.send("Invalid user.")
            return

        if isverified(member):
            await ctx.send("{member.id.mention} is already verified.")
            return

        if isValidMasterAccountName(masteraccount) == False:
            await ctx.send("Invalid MA name")
            return

        if isMasterAccountVerified(masteraccount):
            await ctx.send("MA is already verified")
            return

        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0 WHERE Username = %s", (member.id, masteraccount))
        cursor.close()
        sql.close()

        await member.add_roles(ctx.guild.get_role(verifiedrole))
        await ctx.send("{member.id.mention} has been manually verified as {masteraccount}")

    @commands.command(hidden = True)
    @commands.check(is_management)
    async def unverify(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Invalid user.")
            return

        if not isverified(member):
            await ctx.send("This user is not verified")
            return

        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("DELETE FROM discordroles WHERE discorduser = %s", (member.id, ))
        cursor.execute("UPDATE masters SET discordid = 0 WHERE discordid = %s", (member.id, ))
        cursor.close()
        sql.close()

        roles = []
        for role in member.roles:
            if role.id == rcrpguild: #check to see if the role is @everyone, skip it if so
                continue
            roles.append(role)
        await ctx.send("{member.id.mention} has been unverified.")
        await member.remove_roles(*roles)

    @commands.command(hidden = True)
    @commands.check(is_management)
    async def speak(self, ctx, *, copymessage):
        if len(copymessage) == 0:
            return

        await ctx.message.delete()
        await ctx.send(copymessage)

def setup(bot):
    bot.add_cog(StaffCmdsCog(bot))