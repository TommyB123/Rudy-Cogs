import discord
import aiomysql
import json
from redbot.core import commands
from redbot.core.bot import Red
from datetime import datetime

# weapon names
weaponnames = {
    0: "Fist",
    1: "Brass Knuckles",
    2: "Golf Club",
    3: "Nightstick",
    4: "Knife",
    5: "Baseball Bat",
    6: "Shovel",
    7: "Pool Cue",
    8: "Katana",
    9: "Chainsaw",
    10: "Purple Dildo",
    11: "Small White Vibrator",
    12: "Big White Vibrator",
    13: "Small Silver Vibrator",
    14: "Flowers",
    15: "Cane",
    16: "Grenade",
    17: "Teargas",
    18: "Molotov Cocktail",
    19: "",
    20: "",
    21: "Heavy Armor",
    22: "9mm",
    23: "Silenced Pistol",
    24: "Desert Eagle",
    25: "Shotgun",
    26: "Sawn-off Shotgun",
    27: "SPAS-12",
    28: "Micro Uzi (Mac 10)",
    29: "MP5",
    30: "AK-47",
    31: "M4",
    32: "Tec9",
    33: "Country Rifle",
    34: "Sniper Rifle",
    35: "Rocket Launcher (RPG)",
    36: "Heat-Seeking Rocket Launcher",
    37: "Flamethrower",
    38: "Minigun",
    39: "Satchel Charges",
    40: "Detonator",
    41: "Spray Can",
    42: "Fire Extinguisher",
    43: "Camera",
    44: "Night Vision Goggles",
    45: "Thermal Goggles",
    46: "Parachute",
    47: "",
    48: "",
    49: "",
    50: "",
    51: "",
    52: "",
    53: "",
    54: "",
    55: "Beanbag Shotgun"
}

# various role IDs
adminrole = 293441894585729024
managementrole = 310927289317588992
ownerrole = 293303836125298690
mutedrole = 347541774883094529
verifiedrole = 293441047244308481
helperrole = 293441873945821184
testerrole = 293441807055060993
staffroles = [ownerrole, adminrole, managementrole]

# ID of the rcrp guild
rcrpguildid = 93142223473905664


async def rcrp_check(ctx: commands.Context):
    return ctx.guild is not None and ctx.guild.id == rcrpguildid


async def admin_check(ctx: commands.Context):
    if ctx.guild is not None and ctx.guild.id == rcrpguildid:
        for role in ctx.author.roles:
            if role.id in staffroles:
                return True
        return False
    else:
        return True


async def management_check(ctx: commands.Context):
    if ctx.guild is not None and ctx.guild.id == rcrpguildid:
        role_ids = [role.id for role in ctx.author.roles]
        if managementrole in role_ids or ownerrole in role_ids:
            return True
        else:
            return False
    else:
        return True


def member_is_admin(member: discord.Member):
    for role in member.roles:
        if role.id in staffroles:
            return True
    return False


def member_is_muted(member: discord.Member):
    if mutedrole in [role.id for role in member.roles]:
        return True
    else:
        return False


def member_is_verified(member: discord.Member):
    if verifiedrole in [role.id for role in member.roles]:
        return True
    else:
        return False


class RCRPStaffCommands(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.relay_channel_id = 776943930603470868

    async def send_relay_channel_message(self, ctx: commands.Context, message: str):
        relaychannel = ctx.guild.get_channel(self.relay_channel_id)
        await relaychannel.send(message)

    async def fetch_master_id_from_discord_id(self, discordid: int):
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT id FROM masters WHERE discordid = %s", (discordid, ))
        data = await cursor.fetchone()
        await cursor.close()
        sql.close()

        if data is None:
            return 0
        else:
            return data[0]

    async def fetch_account_id(self, mastername: str):
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT id FROM masters WHERE Username = %s", (mastername, ))
        data = await cursor.fetchone()
        await cursor.close()
        sql.close()

        maid = data[0]
        if maid is None:
            maid = 0
        return maid

    @commands.group()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def lookup(self, ctx: commands.Context):
        """Various search functions"""
        pass

    @lookup.command(name="discord")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def discord_ma_search(self, ctx: commands.Context, discord_user: discord.User):
        """Fetches Master Account info for a verified Discord member"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
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

        embed = discord.Embed(title=f"{data[1]} - {discord_user}", url=f"https://redcountyrp.com/admin/masters/{data[0]}", color=0xe74c3c)
        embed.add_field(name="Account ID", value=data[0], inline=False)
        embed.add_field(name="Username", value=data[1], inline=False)
        embed.add_field(name="Registration Date", value=datetime.utcfromtimestamp(data[2]).strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        embed.add_field(name="Last Login Date", value=datetime.utcfromtimestamp(data[3]).strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        await ctx.send(embed=embed)

    @lookup.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def ma(self, ctx: commands.Context, master_name: str):
        """Fetches a Discord account based on a Master Account name search"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
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

        if data[1] is None or data[1] == 0:
            await ctx.send(f"{master_name} does not have a Discord account linked to their MA.")
            return

        matcheduser = await self.bot.fetch_user(data[1])
        embed = discord.Embed(title=f"{master_name}", url=f"https://redcountyrp.com/admin/masters/{data[0]}", color=0xe74c3c)
        embed.add_field(name="Discord User", value=matcheduser.mention)
        embed.add_field(name="Account ID", value=data[0], inline=False)
        embed.add_field(name="Username", value=master_name, inline=False)
        embed.add_field(name="Registration Date", value=datetime.utcfromtimestamp(data[2]).strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        embed.add_field(name="Last Login Date", value=datetime.utcfromtimestamp(data[3]).strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        await ctx.send(embed=embed)

    @lookup.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def house(self, ctx: commands.Context, *, address: str):
        """Queries the database for information of a house based on user-specified input"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT houses.id, OwnerSQLID, Description, players.Name AS OwnerName, InsideID, ExteriorFurnLimit, Price FROM houses LEFT JOIN players ON players.id = houses.OwnerSQLID WHERE Description LIKE %s", (('%' + address + '%'), ))

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("Invalid house address.")
            return

        if cursor.rowcount > 1:
            await cursor.close()
            sql.close()
            await ctx.send('More than one house was found. Please use a more specific address.')
            return

        house = await cursor.fetchone()
        await cursor.close()
        sql.close()

        if house['OwnerName'] is None:
            if house['OwnerSQLID'] == -5:
                house['OwnerName'] = "Silver Trading"
            else:
                house['OwnerName'] = "Unowned"

        embed = discord.Embed(title=house['Description'], color=0xe74c3c, url=f"https://redcountyrp.com/admin/assets/houses/{house['id']}")
        embed.set_thumbnail(url=f"https://redcountyrp.com/images/houses/{house['id']}.png")
        embed.add_field(name="ID", value=house['id'], inline=False)
        embed.add_field(name="Owner", value=house['OwnerName'], inline=False)
        embed.add_field(name="Price", value='${:,}'.format(house['Price']), inline=False)
        embed.add_field(name="Interior", value=house['InsideID'], inline=False)
        embed.add_field(name="Ext Furn Limit", value=house['ExteriorFurnLimit'], inline=False)
        await ctx.send(embed=embed)

    @lookup.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def business(self, ctx: commands.Context, *, description: str):
        """Queries the database for information of a business based on user-specified input"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT bizz.id, OwnerSQLID, Description, players.Name AS OwnerName, Price, BizzEarnings, IsSpecial, Loaned FROM bizz LEFT JOIN players ON players.id = bizz.OwnerSQLID WHERE Description LIKE %s", (('%' + description + '%'), ))

        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send("Invalid business.")
            return

        if cursor.rowcount > 1:
            await cursor.close()
            sql.close()
            await ctx.send('More than one business was found. Please use a more specific name.')
            return

        bizz = await cursor.fetchone()
        await cursor.close()
        sql.close()

        if bizz['OwnerName'] is None:
            if bizz['OwnerSQLID'] == -5:
                bizz['OwnerName'] = "Silver Trading"
            else:
                bizz['OwnerName'] = "Unowned"

        embed = discord.Embed(title=bizz['Description'], color=0xe74c3c, url=f"https://redcountyrp.com/admin/assets/businesses/{bizz['id']}")
        embed.set_thumbnail(url=f"https://redcountyrp.com/images/businesses/{bizz['id']}.png")
        embed.add_field(name="ID", value=bizz['id'], inline=False)
        embed.add_field(name="Owner", value=bizz['OwnerName'], inline=False)
        embed.add_field(name="Price", value='${:,}'.format(bizz['Price']), inline=False)
        embed.add_field(name="Earnings", value='${:,}'.format(bizz['BizzEarnings']), inline=False)
        embed.add_field(name="Special Int", value='Yes' if bizz['IsSpecial'] == 1 else 'No', inline=False)
        embed.add_field(name="Loaned", value='Yes' if bizz['Loaned'] == 1 else 'No', inline=False)
        await ctx.send(embed=embed)

    @lookup.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def weapons(self, ctx: commands.Context, master_name: str):
        """Collects a list of all the weapons that an account owns"""
        master_id = await self.fetch_account_id(master_name)
        if master_id == 0:
            await ctx.send('Invalid account name.')
            return

        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
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
        embed = discord.Embed(title=f'Weapons of {master_name}', color=0xe74c3c, timestamp=ctx.message.created_at)
        for weapon in data:
            embed.add_field(name=weaponnames[weapon['weapon']], value='{:,}'.format(weapon['count']))
            total += weapon['count']
        embed.add_field(name='Total Weapons', value='{:,}'.format(total))
        await ctx.send(embed=embed)

    @commands.group()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def punish(self, ctx: commands.Context):
        """Issues various punishments to Discord members"""
        pass

    @punish.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def ban(self, ctx: commands.Context, target: discord.Member, *, banreason: str):
        """Issues a ban to a member of the RCRP discord"""
        if member_is_admin(target):
            await ctx.send("You can't ban other staff retard.")
            return

        try:
            embed = discord.Embed(title='Banned', description=f'You have been banned from the Red County Roleplay Discord server by {ctx.author.name}')
            embed.color = 0xe74c3c
            embed.timestamp = ctx.message.created_at
            embed.add_field(name='Ban Reason', value=banreason)
            await target.send(embed=embed)
        except discord.HTTPException:  # an exception will be raised if the bot can't DM the target, so we'll just pass and pretend it never happened
            pass

        baninfo = f"{banreason} - Banned by {ctx.author.name}"
        await ctx.guild.ban(target, reason=baninfo, delete_message_days=0)
        await ctx.send(f"{target.mention} has been successfully banned.")

    @punish.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def unban(self, ctx: commands.Context, target_discordid: int):
        """Removes a ban from the ban list"""
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

    @punish.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def searchban(self, ctx: commands.Context, target_discordid: int):
        """Searches all existing bans for a banned user"""
        banned_user = await self.bot.fetch_user(target_discordid)
        if banned_user is None:
            await ctx.send("Invalid user.")
            return

        bans = await ctx.guild.bans()
        for ban in bans:
            if ban.user.id == banned_user.id:
                await ctx.send(f"{ban.user.mention} was banned for the following reason: {ban.reason}")
                return
        await ctx.send("Could not find any ban info for that user.")

    @punish.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def mute(self, ctx: commands.Context, member: discord.Member):
        """Assigns the muted role to a discord member"""
        if member_is_admin(member):
            await ctx.send("You can't mute other staff.")
            return

        if member_is_muted(member):
            await ctx.send(f"{member.mention} is already muted.")
            return

        await member.add_roles(ctx.guild.get_role(mutedrole))
        await ctx.send(f"{member.mention} has been muted.")

    @punish.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        """Removes the muted role from a discord member"""
        if member_is_admin(member):
            await ctx.send("You can't mute other staff.")
            return

        if not member_is_muted(member):
            await ctx.send(f"{member.mention} is not muted.")
            return

        await member.remove_roles(ctx.guild.get_role(mutedrole))
        await ctx.send(f"{member.mention} has been unmuted.")

    @commands.group()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def assign(self, ctx: commands.Context):
        """Commands for assigning various roles and levels via Discord"""
        pass

    @assign.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def admin(self, ctx: commands.Context, member: discord.Member, level: int):
        """Assigns an admin level and the admin role to a Discord member based on their verified MA."""
        if member_is_verified(member) is False:
            await ctx.send("This command can only be used on verified members. (How would we know what account to give admin to dummy??)")
            return

        if level > 5 or level < 0:
            await ctx.send("Invalid admin level.")
            return

        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
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

    @assign.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def tester(self, ctx: commands.Context, member: discord.Member):
        """Assigns tester status and the tester role to a Discord member based on their verified MA."""
        if member_is_verified(member) is False:
            await ctx.send("This command can only be used on verified members. (How would we know what account to give tester to dummy??)")
            return

        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT Tester FROM masters WHERE discordid = %s", (member.id, ))
        data = await cursor.fetchone()
        tester = ctx.guild.get_role(testerrole)

        if data[0] == 0:  # they're not a tester, let's make them one
            await cursor.execute("UPDATE masters SET Tester = 1 WHERE discordid = %s", (member.id, ))
            await member.add_roles(tester)
            await ctx.send(f'{member.mention} is now a tester!')
        else:
            await cursor.execute("UPDATE masters SET Tester = 0 WHERE discordid = %s", (member.id, ))
            await member.remove_roles(tester)
            await ctx.send(f'{member.mention} is no longer a tester!')

        await cursor.close()
        sql.close()

    @assign.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def helper(self, ctx: commands.Context, member: discord.Member):
        """Assigns helper status and the helper role to a Discord member based on their verified MA."""
        if member_is_verified(member) is False:
            await ctx.send("This command can only be used on verified members. (How would we know what account to give helper to dummy??)")
            return

        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT Helper FROM masters WHERE discordid = %s", (member.id, ))
        data = await cursor.fetchone()
        helper = ctx.guild.get_role(helperrole)

        if data[0] == 0:  # they're not a tester, let's make them one
            await cursor.execute("UPDATE masters SET Helper = 1 WHERE discordid = %s", (member.id, ))
            await member.add_roles(helper)
            await ctx.send(f'{member.mention} is now a helper!')
        else:
            await cursor.execute("UPDATE masters SET Helper = 0 WHERE discordid = %s", (member.id, ))
            await member.remove_roles(helper)
            await ctx.send(f'{member.mention} is no longer a helper!')

        await cursor.close()
        sql.close()

    @assign.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def fc(self, ctx: commands.Context, member: discord.Member):
        """Add or remove Faction Consultant from a member"""
        fcrole = ctx.guild.get_role(393186381306003466)
        if fcrole in [role for role in member.roles]:
            await member.remove_roles(fcrole)
            await ctx.send(f'{member.mention} no longer has the faction consultant role.')
        else:
            await member.add_roles(fcrole)
            await ctx.send(f'{member.mention} now has the faction consultant role.')

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def peaks(self, ctx: commands.Context):
        """Fetches player count peaks for the last 14 days"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT * FROM ucpplayerscron ORDER BY Date DESC LIMIT 14")
        peakdata = await cursor.fetchall()
        await cursor.close()
        sql.close()

        message = []
        for peak in peakdata:
            message.append(f'{peak[0]} - {peak[1]} players\n')

        message = ''.join(message)
        await ctx.send(message)

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def clear(self, ctx: commands.Context, amount: int):
        """Clear up to the last 10 messages"""
        if amount <= 0:
            await ctx.send("Invalid clear count.")
            return

        if amount > 10:
            await ctx.send("You cannot clear more than 10 messages at once.")
            return

        messages = await ctx.channel.history(limit=amount + 1).flatten()
        await ctx.channel.delete_messages(messages)

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def speak(self, ctx: commands.Context, *, copymessage: str):
        """Sends a Discord message as Rudy"""
        if len(copymessage) == 0:
            return

        await ctx.message.delete()
        await ctx.send(copymessage)

    @commands.command()
    @commands.guild_only()
    @commands.check(admin_check)
    async def avatar(self, ctx: commands.Context, member: discord.Member):
        """Fetches the avatar of a Discord member"""
        await ctx.send(f'Avatar of {member.mention}: {member.avatar_url}')

    @commands.group()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def rcrp(self, ctx: commands.Context):
        pass

    @rcrp.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def asay(self, ctx: commands.Context, *, message: str):
        """Broadcasts an admin message in-game"""
        rcrp_message = {
            "callback": "SendDiscordAsay",
            "admin": ctx.author.name,
            "message": message
        }

        await self.send_relay_channel_message(ctx, json.dumps(rcrp_message))

    @rcrp.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def id(self, ctx: commands.Context, *, search: str):
        """Fetches an online player's ID based on user input"""
        rcrp_message = {
            "callback": "SendDiscordIDFetch",
            "target": search,
            "channel": str(ctx.channel.id)
        }

        await self.send_relay_channel_message(ctx, json.dumps(rcrp_message))

    @rcrp.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def igban(self, ctx: commands.Context, target: str, *, reason: str):
        """Bans an online player from the server"""
        master_id = await self.fetch_master_id_from_discord_id(ctx.author.id)
        if master_id == 0:
            return

        rcrp_message = {
            "callback": "SendDiscordBan",
            "admin_id": master_id,
            "admin_name": ctx.author.name,
            "target": target,
            "reason": reason,
            "channel": str(ctx.channel.id)
        }

        await self.send_relay_channel_message(ctx, json.dumps(rcrp_message))

    @rcrp.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(admin_check)
    async def igkick(self, ctx: commands.Context, target: str, *, reason: str):
        """Kicks an online player from the server"""
        master_id = await self.fetch_master_id_from_discord_id(ctx.author.id)
        if master_id == 0:
            return

        rcrp_message = {
            "callback": "SendDiscordKick",
            "admin_id": master_id,
            "admin_name": ctx.author.name,
            "target": target,
            "reason": reason,
            "channel": str(ctx.channel.id)
        }

        await self.send_relay_channel_message(ctx, json.dumps(rcrp_message))
