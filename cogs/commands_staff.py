import discord
import aiomysql
from utility import rcrp_check, admin_check, management_check, member_is_admin, member_is_muted, member_is_verified, mutedrole, testerrole, helperrole, adminrole, mysql_connect, weaponnames, fetch_account_id
from discord.ext import commands
from datetime import datetime

class StaffCmdsCog(commands.Cog, name="Staff"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Clear up to the last 10 messages")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def clear(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("Invalid clear count.")
            return

        if amount > 10:
            await ctx.send("You cannot clear more than 10 messages at once.")
            return

        messages = await ctx.channel.history(limit = amount + 1).flatten()
        await ctx.channel.delete_messages(messages)

    @commands.command(help = "Fetches MA info of a verified discord member")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def whois(self, ctx, discord_user: discord.User):
        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("SELECT id, Username, UNIX_TIMESTAMP(RegTimeStamp) AS RegStamp, LastLog FROM masters WHERE discordid = %s", (discord_user.id, ))
        data = await cursor.fetchone()

        if cursor.rowcount == 0:
            await ctx.send(f"{discord_user} does not have a Master Account linked to their Discord account.")
            await cursor.close()
            sql.close()
            return

        await cursor.close()
        sql.close()

        embed = discord.Embed(title = f"{data[1]} - {discord_user}", url = f"https://redcountyrp.com/admin/masters/{data[0]}", color = 0xe74c3c)
        embed.add_field(name = "Account ID", value = data[0], inline = False)
        embed.add_field(name = "Username", value = data[1], inline = False)
        embed.add_field(name = "Registration Date", value = datetime.utcfromtimestamp(data[2]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        embed.add_field(name = "Last Login Date", value = datetime.utcfromtimestamp(data[3]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
        await ctx.send(embed = embed)

    @commands.command(help = "Fetches the discord account of a member based on their MA name")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def find(self, ctx, master_name: str):
        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("SELECT id, discordid, UNIX_TIMESTAMP(RegTimeStamp) AS RegStamp, LastLog FROM masters WHERE Username = %s", (master_name, ))

        if cursor.rowcount == 0:
            await ctx.send(f"{master_name} is not a valid account name.")
            await cursor.close()
            sql.close()
            return

        data = await cursor.fetchone()
        await cursor.close()
        sql.close()

        if data[1] == None or data[1] == 0:
            await ctx.send(f"{master_name} does not have a Discord account linked to their MA.")
            return

        try:
            matcheduser = await self.bot.fetch_user(data[1])
            embed = discord.Embed(title = f"{master_name}", url = f"https://redcountyrp.com/admin/masters/{data[0]}", color = 0xe74c3c)
            embed.add_field(name = "Discord User", value = matcheduser.mention)
            embed.add_field(name = "Account ID", value = data[0], inline = False)
            embed.add_field(name = "Username", value = master_name, inline = False)
            embed.add_field(name = "Registration Date", value = datetime.utcfromtimestamp(data[2]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
            embed.add_field(name = "Last Login Date", value = datetime.utcfromtimestamp(data[3]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
            await ctx.send(embed = embed)
        except:
            await ctx.send(f"{master_name}'s discord account is no longer valid. Here is the raw ID to see if they're banned and etc: {data[1]}")

    @commands.command(help = "Bans a member from the RCRP discord")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def ban(self, ctx, user: discord.Member, *, banreason: str):
        bannedmember = ctx.guild.get_member(user.id)
        if member_is_admin(bannedmember):
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
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def unban(self, ctx, target_discordid: int):
        banned_user = await self.bot.fetch_user(target_discordid)
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
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def baninfo(self, ctx, target_discordid: int):
        banned_user = await self.bot.fetch_user(target_discordid)
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
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def mute(self, ctx, member: discord.Member):
        if member_is_admin(member):
            await ctx.send("You can't mute other staff.")
            return

        if member_is_muted(member):
            await ctx.send(f"{member.mention} is already muted.")
            return

        await member.add_roles(ctx.guild.get_role(mutedrole))
        await ctx.send(f"{member.mention} has been muted.")

    @commands.command(help = "Unmutes a member")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def unmute(self, ctx, member: discord.Member):
        if member_is_admin(member):
            await ctx.send("You can't mute other staff.")
            return

        if not member_is_muted(member):
            await ctx.send(f"{member.mention} is not muted.")
            return

        await member.remove_roles(ctx.guild.get_role(mutedrole))
        await ctx.send(f"{member.mention} has been unmuted.")

    @commands.command(help = "Sends a message as Rudy")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def speak(self, ctx, *, copymessage: str):
        if len(copymessage) == 0:
            return

        await ctx.message.delete()
        await ctx.send(copymessage)

    @commands.command(help = "Fetches the information of a user specified house")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def house(self, ctx, *, address: str):
        sql = await mysql_connect()
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

        embed = discord.Embed(title = house['Description'], color = 0xe74c3c, url = f"https://redcountyrp.com/admin/characters/{house['OwnerSQLID']}")
        embed.set_thumbnail(url = f"https://redcountyrp.com/images/houses/{house['id']}.png")
        embed.add_field(name = "ID", value = house['id'], inline = False)
        embed.add_field(name = "Owner", value = house['OwnerName'], inline = False)
        embed.add_field(name = "Price", value = '${:,}'.format(house['Price']), inline = False)
        embed.add_field(name = "Interior", value = house['InsideID'], inline = False)
        embed.add_field(name = "Ext Furn Limit", value = house['ExteriorFurnLimit'], inline = False)
        await ctx.send(embed = embed)

    @commands.command(help = "Fetches the information of a user specified business")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def business(self, ctx, *, description: str):
        sql = await mysql_connect()
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

        embed = discord.Embed(title = bizz['Description'], color = 0xe74c3c, url = f"https://redcountyrp.com/admin/characters/{bizz['OwnerSQLID']}")
        embed.set_thumbnail(url = f"https://redcountyrp.com/images/bizz/{bizz['id']}.png")
        embed.add_field(name = "ID", value = bizz['id'], inline = False)
        embed.add_field(name = "Owner", value = bizz['OwnerName'], inline = False)
        embed.add_field(name = "Price", value = '${:,}'.format(bizz['Price']), inline = False)
        embed.add_field(name = "Earnings", value = '${:,}'.format(bizz['BizzEarnings']), inline = False)
        embed.add_field(name = "Special Int", value = 'Yes' if bizz['IsSpecial'] == 1 else 'No', inline = False)
        embed.add_field(name = "Loaned", value = 'Yes' if bizz['Loaned'] == 1 else 'No', inline = False)
        await ctx.send(embed = embed)

    @commands.command(help = "Get the URL of a discord user's avatar")
    @commands.guild_only()
    @commands.check(admin_check)
    async def avatar(self, ctx, member: discord.Member):
        await ctx.send(f'Avatar of {member.mention}: {member.avatar_url}')

    @commands.command(help = "Add or remove Faction Consultant from a member")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def makefc(self, ctx, member: discord.Member):
        fcrole = ctx.guild.get_role(393186381306003466)
        if fcrole in [role for role in member.roles]: #remove
            await member.remove_roles(fcrole)
            await ctx.send(f'{member.mention} no longer has the faction consultant role.')
        else:
            await member.add_roles(fcrole)
            await ctx.send(f'{member.mention} now has the faction consultant role.')

    @commands.command(help = "Hire or fire someone from the tester team")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def maketester(self, ctx, member: discord.Member):
        if member_is_verified(member) == False:
            await ctx.send("The target must be verified.")

        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("SELECT Tester FROM masters WHERE discordid = %s", (member.id, ))
        data = await cursor.fetchone()
        tester = ctx.guild.get_role(testerrole)

        if data[0] == 0: #they're not a tester, let's make them one
            await cursor.execute("UPDATE masters SET Tester = 1 WHERE discordid = %s", (member.id, ))
            await member.add_roles(tester)
            await ctx.send(f'{member.mention} is now a tester!')
        else:
            await cursor.execute("UPDATE masters SET Tester = 0 WHERE discordid = %s", (member.id, ))
            await member.remove_roles(tester)
            await ctx.send(f'{member.mention} is no longer a tester!')

        await cursor.close()
        sql.close()

    @commands.command(help = "Hire or fire someone from the helper team")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def makehelper(self, ctx, member: discord.Member):
        if member_is_verified(member) == False:
            await ctx.send("The target must be verified.")

        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("SELECT Helper FROM masters WHERE discordid = %s", (member.id, ))
        data = await cursor.fetchone()
        helper = ctx.guild.get_role(helperrole)

        if data[0] == 0: #they're not a tester, let's make them one
            await cursor.execute("UPDATE masters SET Helper = 1 WHERE discordid = %s", (member.id, ))
            await member.add_roles(helper)
            await ctx.send(f'{member.mention} is now a helper!')
        else:
            await cursor.execute("UPDATE masters SET Helper = 0 WHERE discordid = %s", (member.id, ))
            await member.remove_roles(helper)
            await ctx.send(f'{member.mention} is no longer a helper!')

        await cursor.close()
        sql.close()

    @commands.command(help = "Set a user's admin level")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def makeadmin(self, ctx, member: discord.Member, level: int):
        if level > 5 or level < 0:
            await ctx.send("Invalid admin level.")
            return

        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET AdminLevel = %s WHERE discordid = %s", (level, member.id))
        await cursor.close()
        sql.close()

        admin = ctx.guild.get_role(adminrole)
        if level == 0:
            await member.remove_roles(admin)
        else:
            await member.add_roles(admin)

        await ctx.send(f'{member.mention} has been assigned admin level {level}')
    
    @commands.command(help = "List all guns that a Master Account owns")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def checkweapons(self, ctx, master_name: str):
        master_id = await fetch_account_id(master_name)
        if master_id == 0:
            await ctx.send('Invalid account name.')
            return

        sql = await mysql_connect()
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT WeaponID AS weapon, COUNT(*) AS count FROM weapons WHERE OwnerSQLID IN (SELECT id FROM players WHERE MasterAccount = %s) AND Deleted = 0 GROUP BY WeaponID", (master_id, ))

        if cursor.rowcount == 0:
            await ctx.send(f'{master_name} does not have any weapons.')
            await cursor.close()
            sql.close()
            return

        data = await cursor.fetchall()
        await cursor.close()
        sql.close()

        total = 0
        embed = discord.Embed(title = f'Weapons of {master_name}', color = 0xe74c3c, timestamp = ctx.message.created_at)
        for weapon in data:
            embed.add_field(name = weaponnames[weapon['weapon']], value = '{:,}'.format(weapon['count']))
            total += weapon['count']
        embed.add_field(name = 'Total Weapons', value = '{:,}'.format(total))
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(StaffCmdsCog(bot))