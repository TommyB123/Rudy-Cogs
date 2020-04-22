import discord
import random
import aiomysql
from random import randint
from config import mysqlconfig

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
rcrpguildid = 93142223473905664

#url of the dashboard. sent to players when they try to verify
dashboardurl = "https://redcountyrp.com/user/dashboard"

#command check decorators
def rcrp_check(ctx):
    if ctx.guild.id == rcrpguildid:
        return True
    else:
        return False

async def admin_check(ctx):
    if ctx.guild.id == rcrpguildid:
        for role in ctx.author.roles:
            if role.id in staffroles:
                return True
        return False
    else:
        return True

async def management_check(ctx):
    if ctx.guild.id == rcrpguildid:
        if managementrole in [role.id for role in ctx.author.roles] or ownerrole in [role.id for role in ctx.author.roles]:
            return True
        else:
            return False
    else:
        return True

def member_is_verified(member):
    if verifiedrole in [role.id for role in member.roles]:
        return True
    else:
        return False

def member_is_admin(member):
    for role in member.roles:
        if role.id in staffroles:
            return True
    return False

def member_is_management(member):
    if managementrole in [role.id for role in member.roles] or ownerrole in [role.id for role in member.roles]:
        return True
    else:
        return False

def member_is_muted(member):
    if mutedrole in [role.id for role in member.roles]:
        return True
    else:
        return False

async def account_is_banned(accountid):
    sql = await aiomysql.connect(** mysqlconfig)
    cursor = await sql.cursor()
    await cursor.execute("SELECT NULL FROM bans WHERE MasterAccount = %s", (accountid, ))
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

async def account_name_valid(name):
    sql = await aiomysql.connect(** mysqlconfig)
    cursor = await sql.cursor()
    await cursor.execute("SELECT NULL FROM masters WHERE Username = %s", (name, ))
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

async def account_verified(name):
    sql = await aiomysql.connect(** mysqlconfig)
    cursor = await sql.cursor()
    await cursor.execute("SELECT NULL FROM masters WHERE Username = %s AND discordid != 0", (name, ))
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

async def account_linked_to_discord(discordid):
    sql = await aiomysql.connect(** mysqlconfig)
    cursor = await sql.cursor()
    await cursor.execute("SELECT NULL FROM masters WHERE discordid = %s", (discordid, ))
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

async def account_accepted(mastername):
    sql = await aiomysql.connect(** mysqlconfig)
    cursor = await sql.cursor()
    await cursor.execute("SELECT NULL FROM masters WHERE Username = %s AND State = 1", (mastername, ))
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True
    
async def mysql_connect():
    return await aiomysql.connect( **mysqlconfig)