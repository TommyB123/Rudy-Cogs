import discord
import asyncio
import random
import mysql.connector
import time

from discord.ext import commands
from imgurpython import ImgurClient
from mysql.connector import errorcode
from random import randint
from datetime import datetime

#discord bot handler
client = commands.Bot(command_prefix='!')

#mysql info
mysqlconfig = {
    'user': 'rcrp_sampserver',
    'password': '1DgBj4QM21p9D2fP62Na5XAeEkkOwi',
    'host': '127.0.0.1',
    'database': 'rcrp_rcrp',
    'raise_on_warnings': True,
}

try:
    sql = mysql.connector.connect(** mysqlconfig)

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Access to MySQL DB denied")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Invalid database")
  else:
    print(err)

sql.close()

#imgur client handler
imclient = ImgurClient('6f85cfd1f822e7b', '629f840ae2bf44b669560b64403c3f8511293777')

#channels where deletions/edits are not logged (management, development, deleted-messages, edited-messages, status)
staffchannels = [412340704187252748, 388002249013460993, 463595960367579137, 463644249108250635, 406166047167741952, 464899293166305291, 445668156824879123, 466946121445539840, 507547199710822400]

#message delete log channel
deletelogs = 463595960367579137

#message edit log channel
editlogs = 463644249108250635

#various server roles
adminrole = 293441894585729024
bannedrole = 592730783924486168
helperrole = 293441873945821184
managementrole = 310927289317588992
mutedrole = 347541774883094529
ownerrole = 293303836125298690
premiumrole = 534479263966167069
rudyfriend = 460848362111893505
testerrole = 293441807055060993
verifiedrole = 293441047244308481

#staff chat server echo channels
adminchat = 397566940723281922
helperchat = 609053396204257290

#all admin+ role IDs
staffroles = [ownerrole, adminrole, managementrole]

#ID of the rcrp guild
rcrpguild = 93142223473905664

#url of the dashboard. sent to players when they try to verify
dashboardurl = "https://redcountyrp.com/user/dashboard"

#the age of rudy. used for the fancy time delta in the age command
rudyage = 1409529600

client.remove_command('help')

def isverified(member):
    if verifiedrole in [role.id for role in member.roles]:
        return True
    else:
        return False

def isadmin(member):
    for role in member.roles:
        if role.id in staffroles:
            return True
    return False

def ismanagement(member):
    if managementrole in [role.id for role in member.roles] or ownerrole in [role.id for role in member.roles]:
        return True
    else:
        return False

async def is_admin(ctx):
    for role in ctx.author.roles:
        if role.id in staffroles:
            return True
    return False

async def is_management(ctx):
    if managementrole in [role.id for role in ctx.author.roles] or ownerrole in [role.id for role in ctx.author.roles]:
        return True
    else:
        return False

def ismuted(member):
    if mutedrole in [role.id for role in member.roles]:
        return True
    else:
        return False

def isbanned(accountid):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()
    cursor.execute("SELECT NULL FROM bans WHERE MasterAccount = %s", (accountid, ))
    data = cursor.fetchone()
    cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

def predicate(message):
    return not message.pinned

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def pretty_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))
    years, seconds = divmod(seconds, 31556952)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if years > 0:
        return '%s%dy %dd %dh %dm %ds' % (sign_string, years, days, hours, minutes, seconds)
    elif days > 0:
        return '%s%dd %dh %dm %ds' % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return '%s%dh %dm %ds' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%dm %ds' % (sign_string, minutes, seconds)
    else:
        return '%s%ds' % (sign_string, seconds)

def isValidMasterAccountName(name):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()
    cursor.execute("SELECT NULL FROM masters WHERE Username = %s", (name, ))
    data = cursor.fetchone()
    cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

def isMasterAccountVerified(name):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()
    cursor.execute("SELECT NULL FROM masters WHERE Username = %s AND discordid != 0", (name, ))
    data = cursor.fetchone()
    cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

def IsDiscordIDLinked(discordid):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()
    cursor.execute("SELECT NULL FROM masters WHERE discordid = %s", (discordid, ))
    data = cursor.fetchone()
    cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

def IsAcceptedMasterAccount(mastername):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()
    cursor.execute("SELECT NULL FROM masters WHERE Username = %s AND State = 1", (mastername, ))
    data = cursor.fetchone()
    cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

async def UpdateSAMPInfo():
    while 1:
        try:
            sql = mysql.connector.connect(** mysqlconfig)
            cursor = sql.cursor()
            cursor.execute("SELECT SUM(Online) AS playercount FROM players WHERE Online = 1")
            data = cursor.fetchone()
            cursor.close()
            sql.close()

            game = discord.Game('RCRP ({data[0]}/200 players)')
            await client.change_presence(activity=game)
        except:
            print("Error while updating player count.")

        await asyncio.sleep(1) #run every second

async def SyncMemberRoles():
    while 1:
        discordguild = client.get_guild(rcrpguild)
        sql = mysql.connector.connect(** mysqlconfig)
        for member in client.get_all_members():
            if not isverified(member):
                continue

            cursor = sql.cursor(dictionary = True)
            cursor.execute("SELECT id, Helper, Tester, AdminLevel, Premium FROM masters WHERE discordid = %s", (member.id, ))
            data = cursor.fetchone()
            cursor.close()

            if data is None:
                continue

            if ismanagement(member):
                continue

            banned = False
            if isbanned(data['id']):
                banned = True

            #remove roles a member shouldn't have
            removeroles = []
            if helperrole in [role.id for role in member.roles] and data['Helper'] == 0: #member isn't a helper but has the role
                removeroles.append(discordguild.get_role(helperrole))
            if testerrole in [role.id for role in member.roles] and data['Tester'] == 0: #member isn't a tester but has the role
                removeroles.append(discordguild.get_role(testerrole))
            if adminrole in [role.id for role in member.roles] and data['AdminLevel'] == 0: #member isn't an admin but has the role
                removeroles.append(discordguild.get_role(adminrole))
            if premiumrole in [role.id for role in member.roles] and data['Premium'] == 0: #member isn't an admin but has the role
                removeroles.append(discordguild.get_role(premiumrole))
            if bannedrole in [role.id for role in member.roles] and banned is False: #member isn't banned but has the role
                removeroles.append(discordguild.get_role(bannedrole))
            if removeroles:
                await member.remove_roles(*removeroles)

            #add roles a member should have
            addroles = []
            if helperrole not in [role.id for role in member.roles] and data['Helper'] == 1: #member is a helper but doesn't have the role
                addroles.append(discordguild.get_role(helperrole))
            if testerrole not in [role.id for role in member.roles] and data['Tester'] == 1: #member is a tester but doesn't have the role
                addroles.append(discordguild.get_role(testerrole))
            if adminrole not in [role.id for role in member.roles] and data['AdminLevel'] != 0: #member is an admin but doesn't have the role
                addroles.append(discordguild.get_role(adminrole))
            if premiumrole not in [role.id for role in member.roles] and data['Premium'] != 0: #member is an admin but doesn't have the role
                addroles.append(discordguild.get_role(premiumrole))
            if bannedrole not in [role.id for role in member.roles] and banned is True: #member isn't banned but has the role
                addroles.append(discordguild.get_role(bannedrole))
            if addroles:
                await member.add_roles(*addroles)
        sql.close()
        await asyncio.sleep(60) #check every minute

async def ProcessMessageQueue():
    while 1:
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor(dictionary = True)
        cursor.execute("SELECT id, channel, message FROM messagequeue WHERE origin = 1 ORDER BY timestamp ASC")

        delete = []
        for message in cursor:
            channel = client.get_channel(int(message['channel']))
            if message['message']:
                await channel.send(message['message'])
            delete.append(message['id'])

        for messageid in delete:
            cursor.execute("DELETE FROM messagequeue WHERE id = %s", (messageid, ))

        sql.commit()
        cursor.close()
        sql.close()
        await asyncio.sleep(1) #checks every second

@client.event
async def on_ready():
    print('\nLogged in as {client.user.name}')
    print(client.user.id)
    print('------')

    client.loop.create_task(SyncMemberRoles())
    client.loop.create_task(UpdateSAMPInfo())
    client.loop.create_task(ProcessMessageQueue())

@client.event
async def on_member_ban(guild, user):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()
    cursor.execute("DELETE FROM discordroles WHERE discorduser = %s", (user.id, ))
    cursor.execute("UPDATE masters SET discordid = 0 WHERE discordid = %s", (user.id, ))
    cursor.close()
    sql.close()

@client.event
async def on_member_join(member):
    discordguild = client.get_guild(rcrpguild)
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()
    cursor.execute("SELECT discordrole FROM discordroles WHERE discorduser = %s", (member.id, ))

    roles = []
    for roleid in cursor:
        role = int(roleid[0])
        if role == rcrpguild: ##check to see if the role is @everyone, skip it if so
            continue
        roles.append(discordguild.get_role(int(roleid[0])))
    await member.add_roles(*roles)

    cursor.close()
    sql.close()

@client.event
async def on_message(message):
    if client.user.id == message.author.id:
        return

    if message.guild is not None:
        await client.process_commands(message)

        if message.channel.id == adminchat or message.channel.id == helperchat:
            queuemessage = "{message.author.name} (discord): {message.content}"
            sql = mysql.connector.connect(** mysqlconfig)
            cursor = sql.cursor()
            cursor.execute("INSERT INTO messagequeue (channel, message, origin, timestamp) VALUES (%s, %s, 2, UNIX_TIMESTAMP())", (message.channel.id, queuemessage))
            sql.commit()
            cursor.close()
            sql.close()
        return

    if message.content.find('verify') == -1:
        await message.author.send("I'm a bot. My only use via direct messages is verifying RCRP accounts. Type 'verify [MA name]' to verify your account.")
        return

    params = message.content.split()
    paramcount = len(params)

    if paramcount == 1: #empty params
        await message.author.send("Usage: verify [Master account name]")
        return

    if IsDiscordIDLinked(message.author.id):
        await message.author.send("This Discord account is already linked to an RCRP account.")
        return

    if paramcount == 2: #entering account name
        if isValidMasterAccountName(params[1]) == False:
            await message.author.send("Invalid account name.")
            return

        if IsAcceptedMasterAccount(params[1]) == False:
            await message.author.send("You cannot verify your Master Account if you have not been accepted into the server.\nIf you're looking for help with the registration process, visit our forums at https://forum.redcountyrp.com")
            return

        code = random_with_N_digits(10)
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("UPDATE masters SET discordcode = %s WHERE Username = %s AND discordid = 0", (str(code), params[1]))
        cursor.close()
        sql.close()

        await message.author.send("Your verification code has been set! Log in on our website and look for 'Discord Verification Code' at your dashboard page. ({dashboardurl})\nOnce you have found your verification code, send 'verify {params[1]} [code]' to confirm your account.")
    elif paramcount == 3: #entering code
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("SELECT COUNT(*), id, Helper, Tester, AdminLevel AS results FROM masters WHERE discordcode = %s AND Username = %s", (params[2], params[1]))
        data = cursor.fetchone()
        cursor.close()

        if data[0] == 0: #account doesn't match
            await message.author.send("Invalid ID.")
            return

        discordguild = client.get_guild(rcrpguild)
        discordmember = discordguild.get_member(message.author.id)
        discordroles = []
        discordroles.append(discordguild.get_role(verifiedrole))
        if data[2] == 1: #guy is helper
            discordroles.append(discordguild.get_role(helperrole))
        if data[3] == 1: #guy is tester
            discordroles.append(discordguild.get_role(testerrole))
        if data[4] != 0: #guy is admin
            discordroles.append(discordguild.get_role(adminrole))
        if data[4] == 4: #guy is management
            discordroles.append(discordguild.get_role(managementrole))
        await discordmember.add_roles(*discordroles)

        cursor = sql.cursor()
        cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0 WHERE id = %s", (message.author.id, data[1]))
        cursor.close()
        sql.close()

        await message.author.send("Your account is now verified!")
    else:
        await message.author.send("Usage: verify [Master account name]")

@client.event
async def on_message_delete(message):
    if message.author.id == 311318305564655637: #mussy's id
        em=discord.Embed(title='Message Deleted', description="Mussy deleted a message like a bitch. Let's see what it was!", color = 0xe74c3c, timestamp = message.created_at)
        em.add_field(name='Message Content', value=message.content, inline=False)
        em.set_author(name=message.author, icon_url=message.author.avatar_url)
        em.set_footer(text="User ID: {message.author.id}")
        await message.channel.send(embed=em)

    if message.channel.id not in staffchannels and message.guild is not None:
        deletechan = client.get_channel(deletelogs)
        em=discord.Embed(title='Message Deleted', description='Message by {message.author.mention} in {message.channel.mention} was deleted', color = 0xe74c3c, timestamp = message.created_at)
        em.add_field(name='Message Content', value=message.content, inline=False)
        em.set_author(name=message.author, icon_url=message.author.avatar_url)
        em.set_footer(text="User ID: {message.author.id}")
        await deletechan.send(embed=em)

@client.event
async def on_message_edit(before, after):
    if before.channel.id not in staffchannels and before.guild is not None:
        if before.content == after.content:
            return

        editchan = client.get_channel(editlogs)
        em=discord.Embed(title='Message Edited', description='{before.author.mention} edited a message in {before.channel.mention}', color = 0xe74c3c, timestamp = after.edited_at)
        em.add_field(name='Original Message', value=before.content, inline=False)
        em.add_field(name='New Message', value=after.content, inline=False)
        em.set_author(name=after.author, icon_url=after.author.avatar_url)
        em.set_footer(text="User ID: {after.author.id}")
        await editchan.send(embed=em)

@client.event
async def on_member_update(before, after):
    if not isverified(after) or before.roles == after.roles:
        return

    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()

    #check for removed roles and delete them
    for role in before.roles:
        if role.id not in after.roles:
            cursor.execute("DELETE FROM discordroles WHERE discorduser = %s AND discordrole = %s", (before.id, role.id))
    cursor.close()

    #check for added roles and insert them
    cursor = sql.cursor()
    for role in after.roles:
        if role.id not in before.roles:
            if role.id == rcrpguild: #check to see if role is @everyone, skip it if so
                continue;
            cursor.execute("INSERT INTO discordroles (discorduser, discordrole) VALUES (%s, %s)", (before.id, role.id))
            sql.commit()

    cursor.close()
    sql.close()

@client.command(help = "Sends an adorable picture of Rudy")
async def rudypic(ctx):
    if rudyfriend in [role.id for role in ctx.author.roles]:
        pictures = []
        for image in imclient.get_album_images('WLQku0l'):
            pictures.append(image.link)
        await ctx.send(random.choice(pictures))
    else:
        await ctx.message.delete()

@client.command(help = "Gives Rudy a number of different items")
async def give(ctx, item = 'none'):
    if item == 'poptart':
        await ctx.send("* Rudy enjoys the poptart but vomits it back up about twenty minutes later. * (this actually happened i fucking hate my sister)")
    elif item == 'treat':
        await ctx.send("* Rudy takes the treat from your hand and runs off into another room with it, more than likely a room that has carpet. He chews on the treat clumsily, creating a mess of crumbs on the floor. He eventually sniffs out the crumbs he failed to ingest and finishes off every last one. *")
    elif item == 'bone':
        await ctx.send("* Rudy happily takes the bone from you and runs off with it, however he neglects to actually chew on said bone. He instead leaves the bone in an accessible location at all times and waits for moments of opportune happiness or excitement (e.g, someone returning home) to put it back in his mouth. Once peak excitement levels are reached, he prances around the house with the bone in his mouth, doing multiple laps around the kitchen with it as well. *")
    else:
        await ctx.send("*Rudy stares at your empty hand disappointed. *")

@client.command(hidden = True)
@commands.check(is_admin)
async def clear(ctx, *, amount : int = 0):
    if amount == 0:
        return

    if amount > 10:
        await ctx.send("You cannot clear more than 10 messages at once.")
        return

    messages = await ctx.channel.history(limit = amount + 1).flatten()
    await ctx.channel.delete_messages(messages)

@client.command(hidden = True)
@commands.is_owner()
async def dms(ctx):
    await ctx.send("<https://imgur.com/a/yYK5dnZ>")

@client.command(help = "Give Rudy some pets")
async def pet(ctx, *, location: str = 'None'):
    if location == 'head' or location == 'ears':
        await ctx.send("* You pet Rudy's head, specifically behind the ears. He enjoys this very much and sticks his nose out directly towards you as a reaction to the affection. *")
    elif location == 'lower back':
        await ctx.send("* You give Rudy a nice petting on his lower back, maybe sneaking in some back scratches too. He enjoys this very much and pokes his nose into the air as a reaction to the affection. *")
    else:
        await ctx.send("*You pet Rudy. He thinks it's pretty neat. *")

@client.command(hidden = True)
async def clearapps(ctx):
    if ctx.channel.id == 445668156824879123:
        messages = await ctx.channel.history().filter(predicate).flatten()
        await ctx.channel.delete_messages(messages)

@client.command(hidden = True)
@commands.check(is_admin)
async def whois(ctx, user: discord.User=None):
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

@client.command(hidden = True)
@commands.check(is_admin)
async def find(ctx, name : str = 'None'):
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

    matcheduser = await client.fetch_user(data[1])
    embed = discord.Embed(title = "{name}", url = "https://redcountyrp.com/admin/masters/{data[0]}", color = 0xe74c3c)
    embed.add_field(name = "Discord User", value = matcheduser.id.mention)
    embed.add_field(name = "Account ID", value = data[0], inline = False)
    embed.add_field(name = "Username", value = name, inline = False)
    embed.add_field(name = "Registration Date", value = datetime.utcfromtimestamp(data[2]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
    embed.add_field(name = "Last Login Date", value = datetime.utcfromtimestamp(data[3]).strftime('%Y-%m-%d %H:%M:%S'), inline = False)
    await ctx.send(embed = embed)

@client.command(hidden = True)
@commands.check(is_admin)
async def ban(ctx, user: discord.User = None, *, banreason):
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
        adminuser = await client.fetch_user(ctx.author.id)
        embed = discord.Embed(title = 'Banned', description = 'You have been banned from the Red County Roleplay Discord server by {adminuser.name}', color = 0xe74c3c, timestamp = ctx.message.created_at)
        embed.add_field(name = 'Ban Reason', value = banreason)
        await user.send(embed = embed)
    except:
        print("couldn't ban user because dms off")

    baninfo = "{banreason} - Banned by {adminuser.name}"
    await ctx.guild.ban(bannedmember, reason = baninfo, delete_message_days = 0)
    await ctx.send("{bannedmember.id.mention} has been successfully banned.")

@client.command(hidden = True)
@commands.check(is_admin)
async def unban(ctx, target):
    banned_user = await client.fetch_user(target)
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

@client.command(hidden = True)
@commands.check(is_admin)
async def baninfo(ctx, target: str = ""):
    banned_user = await client.fetch_user(target)
    if not banned_user:
        await ctx.send("Invalid user.")
        return

    bans = await ctx.guild.bans()
    for ban in bans:
        if ban.user.id == banned_user.id:
            await ctx.send("{ban.user.mention} was banned for the following reason: {ban.reason}")
            return
    await ctx.send("Could not find any ban info for that user.")

@client.command(hidden = True)
@commands.check(is_admin)
async def mute(ctx, member: discord.Member = None):
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

@client.command(hidden = True)
@commands.check(is_admin)
async def unmute(ctx, member: discord.Member = None):
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

@client.command(hidden = True)
@commands.check(is_management)
async def verify(ctx, member: discord.Member = None, masteraccount: str = " "):
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

@client.command(hidden = True)
@commands.check(is_management)
async def unverify(ctx, member: discord.Member = None):
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

@client.command(help = "Displays the age of Rudy")
async def age(ctx):
    rudy_age = pretty_time_delta(int(time.time()) - rudyage)
    await ctx.send("Rudy's age: {rudy_age}")

@client.command(hidden = True)
@commands.check(is_admin)
async def admins(ctx):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor(buffered = True, dictionary = True)
    cursor.execute("SELECT masters.Username AS mastername, players.Name AS charactername FROM masters JOIN players ON players.MasterAccount = masters.id WHERE AdminLevel != 0 AND Online = 1")

    if cursor.rowcount == 0:
        cursor.close()
        sql.close()
        await ctx.send("There are currently no admins ingame.")
        return

    embed = discord.Embed(title = 'Ingame Administrators', color = 0xe74c3c, timestamp = ctx.message.created_at)

    for admininfo in cursor:
        embed.add_field(name = admininfo['mastername'], value = admininfo['charactername'], inline = True)

    cursor.close()
    sql.close()
    await ctx.send(embed = embed)

@client.command(hidden = True)
@commands.check(is_admin)
async def helpers(ctx):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor(buffered = True, dictionary = True)
    cursor.execute("SELECT masters.Username AS mastername, players.Name AS charactername FROM masters JOIN players ON players.MasterAccount = masters.id WHERE Helper != 0 AND Online = 1")

    if cursor.rowcount == 0:
        cursor.close()
        sql.close()
        await ctx.send("There are currently no helpers ingame.")
        return

    embed = discord.Embed(title = 'Ingame Helpers', color = 0xe74c3c, timestamp = ctx.message.created_at)

    for helperinfo in cursor:
        embed.add_field(name = helperinfo['mastername'], value = helperinfo['charactername'], inline = False)

    cursor.close()
    sql.close()
    await ctx.send(embed = embed)

@client.command(hidden = True)
@commands.check(is_management)
async def speak(ctx, *, copymessage):
    if len(copymessage) == 0:
        return

    await ctx.message.delete()
    await ctx.send(copymessage)

#simple no parameter/perm check commands
@client.command(help = "Gives a kind response about Rudy's weight")
async def makerudyfat(ctx):
   await ctx.send("Rudy can't be fat you fucking subhuman piece of shit.")

@client.command(help = "Gives Rudy a nice bellyrub!")
async def bellyrub(ctx):
   await ctx.send("* You give Rudy a bellyrub. He kicks at your hand like a fucking idiot. *")

@client.command(help = "Takes Rudy for a walk")
async def walk(ctx):
   await ctx.send("* Upon hearing news of a potential walk, Rudy fucking loses his shit and starts to jump at you like a madman. He pants heavily while jumping at you repeatedly until you hopefully grab his leash and take him on a nice walk through the nearby park. *")

@client.command(help = "Displays the weight of Rudy.")
async def weight(ctx):
   await ctx.send("I weigh 12 pounds. (5.44 KG or 0.85 stone for foreign people)")

@client.command(help = "Orders Rudy to sit")
async def sit(ctx):
   await ctx.send("* Rudy obediently sits down like a good boy. His tail wags back and forth a few times as well. *")

@client.command(help = "Orders Rudy to stay")
async def stay(ctx):
   await ctx.send("* Rudy sits down at his current position with one ear straight up and the other floppy. He eventually gets dog brain syndrome and stands up, following you. *")

@client.command(help = "A terrible story from a terrible night")
async def brisket(ctx):
   await ctx.send("Once upon a time, I wad fed copious amounts of delicious brisket by a drunk man. I have a really sensitive stomach and I'm only supposed to eat special dog food which helps relax it. During the middle of the night when I was asleep, I felt a pain in my stomach and started to cough and gag a bunch. My owner woke up due to the sounds and quickly rushed me into the kitchen in hopes to take me outside. I then proceeded to projectile vomit on the floor several times, it was not a fun experience. My poor owner had to clean up the mess I created. I haven't been fed table food since.")

@client.command(help = "A terrible story about some rabbits")
async def rabbits(ctx):
   await ctx.send("Once upon a time, there was a rabbit that kept intruding in the back yard every once in a while. Every time I noticed it, I would sprint off towards it for reasons my dog brain can't explain. One day I was sniffing around the yard and noticed a bunch of little baby rabbits in a hole dug in MY YARD. My instinctive dog reaction was to murder every single little rabbit that I could find. I even ripped two of them in half with my dog teeth.")

@client.command(help = "Give Rudy a bath!")
async def bathe(ctx):
    await ctx.send("* You give Rudy a bath. He dislikes it heavily. *")

@client.command(hidden = True)
async def unixtimestamp(ctx):
    time = int(time.time())
    await ctx.send("CURRENT UNIX TIMESTAMP VALUE: {time}")

client.run("MzAwMDk4MzYyNTI5NTQ2MjQw.DiIZ3w.pU08PJVTvxqfwF-NpunCEeRigd0", reconnect=True)