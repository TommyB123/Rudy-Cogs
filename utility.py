import discord
import random
import mysqlinfo
import mysql.connector
from random import randint

class rcrp_utility:
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

    def appfilter(message):
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