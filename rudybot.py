import discord
import asyncio
import random
import mysql.connector
import time

from discord.ext import commands
from samp_client import constants
from samp_client.client import SampClient
from imgurpython import ImgurClient
from mysql.connector import errorcode
from random import randint

#discord bot handler
client = commands.Bot(command_prefix='!')

#mysql info
mysqlconfig = {
    'user': 'rcrp_sampserver',
    'password': '.MRi#z(1IsTH',
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

#all admin+ role IDs
staffroles = [293303836125298690, 293441894585729024, 310927289317588992]

#role ID for the verified role
verifiedrole = 293441047244308481
rudyfriend = 460848362111893505

#helper role ID
helperrole = 293441873945821184
testerrole = 293441807055060993
adminrole = 293441894585729024
managementrole = 310927289317588992
ownerrole = 293303836125298690
premiumrole = 534479263966167069

#ID of the rcrp guild
rcrpguild = 93142223473905664

dashboardurl = "https://redcountyrp.com/user/dashboard"

rudyage = 1409529600

client.remove_command('help')

async def UpdateSAMPInfo():
    while 1:
        try:
            with SampClient(address = 'server.redcountyrp.com', port = 7777) as samp:
                if samp is not None:
                    sampinfo = samp.get_server_info()
                    game = discord.Game('RCRP (%i/%i players)' % (sampinfo.players, sampinfo.max_players))
                    await client.change_presence(activity=game)
        except:
            game = discord.Game('RCRP (currently down)')
            await client.change_presence(activity=game)
        await asyncio.sleep(5) #run every 5 seconds

def isverified(user):
    if verifiedrole in [role.id for role in user.roles] or rudyfriend in [role.id for role in user.roles]:
        return True
    else:
        return False

def isadmin(user):
    for role in user.roles:
        if role.id in staffroles:
            return True
    return False

def ismanagement(user):
    if managementrole in [role.id for role in user.roles] or ownerrole in [role.id for role in user.roles]:
        return True
    else:
        return False

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

async def SyncMemberRoles():
    while 1:
        discordguild = client.get_guild(rcrpguild)
        sql = mysql.connector.connect(** mysqlconfig)
        for member in client.get_all_members():
            if isverified(member):
                cursor = sql.cursor()
                cursor.execute("SELECT Helper, Tester, AdminLevel, Premium FROM masters WHERE discordid = %s", (member.id, ))
                data = cursor.fetchone()
                cursor.close()

                if data is None:
                    continue

                if not ismanagement(member):
                    #remove roles a member shouldn't have
                    removeroles = []
                    if helperrole in [role.id for role in member.roles] and data[0] == 0: #member isn't a helper but has the role
                        removeroles.append(discordguild.get_role(helperrole))
                    if testerrole in [role.id for role in member.roles] and data[1] == 0: #member isn't a tester but has the role
                        removeroles.append(discordguild.get_role(testerrole))
                    if adminrole in [role.id for role in member.roles] and data[2] == 0: #member isn't an admin but has the role
                        removeroles.append(discordguild.get_role(adminrole))
                    if premiumrole in [role.id for role in member.roles] and data[3] == 0: #member isn't an admin but has the role
                        removeroles.append(discordguild.get_role(premiumrole))
                    if removeroles:
                        await member.remove_roles(*removeroles)

                    #add roles a member should have
                    addroles = []
                    if helperrole not in [role.id for role in member.roles] and data[0] == 1: #member is a helper but doesn't have the role
                        addroles.append(discordguild.get_role(helperrole))
                    if testerrole not in [role.id for role in member.roles] and data[1] == 1: #member is a tester but doesn't have the role
                        addroles.append(discordguild.get_role(testerrole))
                    if adminrole not in [role.id for role in member.roles] and data[2] != 0: #member is an admin but doesn't have the role
                        addroles.append(discordguild.get_role(adminrole))
                    if premiumrole not in [role.id for role in member.roles] and data[3] != 0: #member is an admin but doesn't have the role
                        addroles.append(discordguild.get_role(premiumrole))
                    if addroles:
                        await member.add_roles(*addroles)
        sql.close()
        await asyncio.sleep(120) #check every 2 minutes

@client.event
async def on_ready():
    print('\nLogged in as {0}'.format(client.user.name))
    print(client.user.id)
    print('------')

    client.loop.create_task(SyncMemberRoles())
    client.loop.create_task(UpdateSAMPInfo())

@client.event
async def on_member_ban(guild, user):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()
    cursor.execute("DELETE FROM discordroles WHERE discorduser = %s", (member.id, ))
    cursor.execute("UPDATE masters SET discordid = NULL WHERE discordid = %s", (member.id))
    cursor.close()
    sql.close()

@client.event
async def on_member_join(member):
    sql = mysql.connector.connect(** mysqlconfig)
    cursor = sql.cursor()
    cursor.execute("SELECT discordrole FROM discordroles WHERE discorduser = %s", (member.id, ))
    discordguild = client.get_guild(rcrpguild)
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

    if message.guild is None:
        if message.content.find('verify') != -1:
            list = message.content.split()
            listcount = len(list)

            sql = mysql.connector.connect(** mysqlconfig)
            cursor = sql.cursor()
            cursor.execute("SELECT COUNT(*) FROM masters WHERE discordid = %s", (message.author.id,))
            data = cursor.fetchone()
            cursor.close()
            if data[0] == 0: #account not verified
                if listcount == 1: #empty params
                    await message.author.send(message.author, "Usage: verify [Master account name]")
                if listcount > 1:
                    if list[1] != "verify":
                        if listcount == 2: #entering account name
                            cursor = sql.cursor()
                            cursor.execute("SELECT COUNT(*), State FROM masters WHERE Username = %s", (list[1],))
                            data = cursor.fetchone()
                            if data[0] != 0: #account with name found
                                if data[1] == 1: #account is an accepted MA
                                    code = random_with_N_digits(10)
                                    cursor = sql.cursor()
                                    cursor.execute("UPDATE masters SET discordcode = %s WHERE Username = %s AND discordid IS NULL", (str(code), list[1]))
                                    cursor.close()
                                    await message.author.send("Your verification code has been set! Log in on our website and look for 'Discord Verification Code' at your dashboard page. ({0})\nOnce you have found your verification code, send 'verify {1} [code]' to confirm your account.".format(dashboardurl, list[1]))
                                else:
                                    await message.author.send("You cannot verify your Master Account if you have not been accepted into the server.\nIf you're looking for help with the registration process, visit our forums at https://forum.redcountyrp.com")
                            else:
                                await message.author.send("Invalid account name.")
                        elif listcount == 3: #entering code
                            cursor = sql.cursor()
                            cursor.execute("SELECT COUNT(*), id, Helper, Tester, AdminLevel AS results FROM masters WHERE discordcode = %s AND Username = %s", (list[2], list[1]))
                            data = cursor.fetchone()
                            cursor.close()
                            if data[0] == 1: #account match
                                discordguild = client.get_guild(rcrpguild)
                                discordmember = discordguild.get_member(message.author.id)
                                discordroles = []
                                discordroles.append(discord.utils.get(discordguild.roles, id = verifiedrole))
                                if data[2] == 1: #guy is helper
                                    discordroles.append(discord.utils.get(discordguild.roles, id = helperrole))
                                if data[3] == 1: #guy is tester
                                    discordroles.append(discord.utils.get(discordguild.roles, id = testerrole))
                                if data[4] != 0: #guy is admin
                                    discordroles.append(discord.utils.get(discordguild.roles, id = adminrole))
                                if data[4] == 4: #guy is management
                                    discordroles.append(discord.utils.get(discordguild.roles, id = managementrole))
                                await member.add_roles(*discordroles)
                                cursor = sql.cursor()
                                cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0 WHERE id = %s", (message.author.id, data[1]))
                                cursor.close()
                                await message.author.send("Your account is now verified!")
                            else:
                                await message.author.send("Invalid ID.")
                        else:
                            await message.author.send("Usage: verify [Master account name]")
            else:
                await message.author.send("That account is already linked to a discord account.")
            sql.close()
        else:
            message.author.send("I'm a bot. My only use via direct messages is verifying RCRP accounts. Type 'verify [MA name]' to verify your account.")
    else:
        await client.process_commands(message)

@client.event
async def on_message_delete(message):
    if message.channel.id not in staffchannels and message.guild is not None:
        deletechan = client.get_channel(deletelogs)
        em=discord.Embed(title='Message Deleted', description='Message by <@{0}> in <#{1}> was deleted'.format(message.author.id, message.channel.id), color = 0x1abc9c, timestamp = message.created_at)
        em.add_field(name='Message Content', value=message.content, inline=False)
        em.set_author(name=message.author, icon_url=message.author.avatar_url)
        em.set_footer(text="User ID: {0}".format(message.author.id))
        await deletechan.send(embed=em)

@client.event
async def on_message_edit(before, after):
    if before.channel.id not in staffchannels and before.guild is not None:
        if before.content == after.content:
            return

        editchan = client.get_channel(editlogs)
        em=discord.Embed(title='Message Edited', description='<@{0}> edited a message in <#{1}>'.format(before.author.id, before.channel.id), color = 0x1abc9c, timestamp = after.edited_at)
        em.add_field(name='Original Message', value=before.content, inline=False)
        em.add_field(name='New Message', value=after.content, inline=False)
        em.set_author(name=after.author, icon_url=after.author.avatar_url)
        em.set_footer(text="User ID: {0}".format(after.author.id))
        await editchan.send(embed=em)

@client.event
async def on_member_update(before, after):
    if isverified(after):
        if before.roles != after.roles:
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

@client.command()
async def rudypic(ctx):
    if rudyfriend in [role.id for role in ctx.author.roles]:
        pictures = []
        for image in imclient.get_album_images('WLQku0l'):
            pictures.append(image.link)
        await ctx.send(random.choice(pictures))
    else:
        await ctx.send("You can't do that.")

@client.command()
async def give(ctx, item = 'none'):
    if item == 'poptart':
        await ctx.send("* Rudy enjoys the poptart but vomits it back up about twenty minutes later. * (this actually happened i fucking hate my sister)")
    elif item == 'treat':
        await ctx.send("* Rudy takes the treat from your hand and runs off into another room with it, more than likely a room that has carpet. He chews on the treat clumsily, creating a mess of crumbs on the floor. He eventually sniffs out the crumbs he failed to ingest and finishes off every last one. *")
    elif item == 'bone':
        await ctx.send("* Rudy happily takes the bone from you and runs off with it, however he neglects to actually chew on said bone. He instead leaves the bone in an accessible location at all times and waits for moments of opportune happiness or excitement (e.g, someone returning home) to put it back in his mouth. Once that happens, he prances around the house with the bone in his mouth, doing multiple laps around the kitchen with it as well. *")
    else:
        await ctx.send("*Rudy stares at your empty hand disappointed. *")

@client.command()
async def clear(ctx, *, amount : int = 0):
    if amount == 0:
        return

    if isadmin(ctx.author):
        if amount > 10:
            await client.say("You cannot clear more than 10 messages at once.")
            return

        messages = await ctx.channel.history(limit = amount + 1).flatten()
        await ctx.channel.delete_messages(messages)

@client.command()
async def dms(ctx):
    if ctx.author.id == 87582156741681152: #tommyb id
        await ctx.send("https://imgur.com/a/yYK5dnZ")

@client.command()
async def pet(ctx, *, location: str = 'None'):
    if location == 'head' or location == 'ears':
        await ctx.send("* You pet Rudy's head, specifically behind the ears. He enjoys this very much and sticks his nose out directly towards you as a reaction to the affection. *")
    elif location == 'lower back':
        await ctx.send("* You give Rudy a nice petting on his lower back, maybe sneaking in some back scratches too. He enjoys this very much and pokes his nose into the air as a reaction to the affection. *")
    else:
        await ctx.send("*You pet Rudy. He thinks it's pretty neat. *")

@client.command()
async def clearapps(ctx):
    if ctx.channel.id == 445668156824879123:
        messages = await ctx.channel.history().filter(predicate).flatten()
        await ctx.channel.delete_messages(messages)

@client.command()
async def whois(ctx, user: discord.User=None):
    if isadmin(ctx.author):
        if not user:
            await ctx.send("Invalid user.")
        else:
            sql = mysql.connector.connect(** mysqlconfig)
            cursor = sql.cursor()
            cursor.execute("SELECT id, Username FROM masters WHERE discordid = %s", (user.id, ))
            data = cursor.fetchone()
            if cursor.rowcount != 0:
                await ctx.send("Master Account of {0}: {1} (https://redcountyrp.com/admin/masters/{2})".format(user, data[1], data[0]))
            else:
                await ctx.send("{0} does not have a Master Account linked to their Discord account.".format(user))
            cursor.close()
            sql.close()

@client.command()
async def find(ctx, name : str = 'None'):
    if isadmin(ctx.author):
        if name != 'None':
            sql = mysql.connector.connect(** mysqlconfig)
            cursor = sql.cursor()
            cursor.execute("SELECT discordid FROM masters WHERE Username = %s", (name, ))
            data = cursor.fetchone()
            if cursor.rowcount != 0:
                if data[0] == None:
                    await ctx.send("{0} does not have a Discord account linked to their MA.".format(name))
                else:
                    member = discord.utils.get(ctx.guild.members, id = data[0])
                    await ctx.send("Discord Account of {0}: <@{1}>".format(name, member.id))
            else:
                await ctx.send("{0} is not a valid account name.".format(name))
            cursor.close()
            sql.close()

@client.command()
async def lookup(ctx, id : str = 'None'):
    if isadmin(ctx.author) and id != 'None':
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("SELECT Username FROM masters WHERE discordid = %s", (id, ))
        data = cursor.fetchone()
        if cursor.rowcount != 0:
            await ctx.send("Master Account of Discord ID {0}: {1}".format(id, data[0]))
        cursor.close()
        sql.close()

@client.command()
async def ban(ctx, user: discord.User = None, *reason: str):
    if isadmin(ctx.author):
        str = []
        for value in reason:
            str.append(value)
        banreason = ' '.join(str)
        if not user:
            await ctx.send("Invalid user.")
            return
        if len(banreason) == 0:
            await ctx.send("Enter a reason.")
            return
        if isadmin(user):
            await ctx.send("You can't ban other staff idiot boy.")
            return
        adminuser = await client.get_user_info(ctx.author.id)
        em = discord.Embed(title = 'Banned', description = 'You have been banned from the Red County Roleplay Discord server by {0}'.format(adminuser.name), color = 0xe74c3c)
        em.add_field(name = 'Ban Reason', value = banreason, inline = False)
        em.timestamp = ctx.message.timestamp
        await user.send(embed = em)
        await ctx.guild.ban(user, 0, Reason = str)
        await ctx.send("<@{0}> has been successfully banned.".format(user.id))

@client.command()
async def age(ctx):
    rudy_age = pretty_time_delta(int(time.time()) - rudyage)
    await ctx.send("Rudy's age: {0}".format(rudy_age))

#simple no parameter/perm check commands
@client.command()
async def makerudyfat(ctx):
   await ctx.send("Rudy can't be fat you fucking subhuman piece of shit.")

@client.command()
async def bellyrub(ctx):
   await ctx.send("* You give Rudy a bellyrub. He kicks at your hand like a fucking idiot. *")

@client.command()
async def walk(ctx):
   await ctx.send("* Upon hearing news of a potential walk, Rudy fucking loses his shit and starts to jump at you like a madman. He pants heavily while jumping at you repeatedly until you hopefully grab his leash and take him on a nice walk through the nearby park. *")

@client.command()
async def weight(ctx):
   await ctx.send("I weigh 12 pounds. (5.44 KG or 0.85 stone for foreign people)")

@client.command()
async def brooks(ctx):
    pictures = []
    for image in imclient.get_album_images('hWatGWe'):
        pictures.append(image.link)
    await ctx.send("* Downstairs borks from dog friend Mr. Brooks *\n {0}".format(random.choice(pictures)))

@client.command()
async def sit(ctx):
   await ctx.send("* Rudy obediently sits down like a good boy. His tail wags back and forth a few times as well. *")

@client.command()
async def stay(ctx):
   await ctx.send("* Rudy sits down at his current position with one ear straight up and the other floppy. He eventually gets dog brain syndrome and stands up, following you. *")

@client.command()
async def brisket(ctx):
   await ctx.send("Once upon a time, I wad fed copious amounts of delicious brisket by a drunk man. I have a really sensitive stomach and I'm only supposed to eat special dog food which helps relax it. During the middle of the night when I was asleep, I felt a pain in my stomach and started to cough and gag a bunch. My owner woke up due to the sounds and quickly rushed me into the kitchen in hopes to take me outside. I then proceeded to projectile vomit on the floor several times, it was not a fun experience. My poor owner had to clean up the mess I created. I haven't been fed table food since.")

@client.command()
async def rabbits(ctx):
   await ctx.send("Once upon a time, there was a rabbit that kept intruding in the back yard every once in a while. Every time I noticed it, I would sprint off towards it for reasons my dog brain can't explain. One day I was sniffing around the yard and noticed a bunch of little baby rabbits in a hole dug in MY YARD. My instinctive dog reaction was to murder every single little rabbit that I could find. I even ripped two of them in half with my dog teeth.")

@client.command()
async def bathe(ctx):
    await ctx.send("* You give Rudy a bath. He dislikes it heavily. *")

@client.command()
async def unixtimestamp(ctx):
    await ctx.send("CURRENT UNIX TIMESTAMP VALUE: {0}".format(int(time.time())))


client.run("MzAwMDk4MzYyNTI5NTQ2MjQw.DiIZ3w.pU08PJVTvxqfwF-NpunCEeRigd0")