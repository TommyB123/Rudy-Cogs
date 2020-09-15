import discord
import random
import aiomysql
from redbot.core import commands
from random import randint
from .config import mysqlconfig

#weapon names
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
frostgamingguild = 93140261797904384

#url of the dashboard. sent to players when they try to verify
dashboardurl = "https://redcountyrp.com/user/dashboard"

#command check decorators
def rcrp_check(ctx: commands.Context):
    if ctx.guild.id == rcrpguildid:
        return True
    else:
        return False

def rudy_check(ctx: commands.Context):
    if ctx.guild.id in [rcrpguildid, frostgamingguild]:
        return True
    else:
        return False

async def admin_check(ctx: commands.Context):
    if ctx.guild.id == rcrpguildid:
        for role in ctx.author.roles:
            if role.id in staffroles:
                return True
        return False
    else:
        return True

async def management_check(ctx: commands.Context):
    if ctx.guild.id == rcrpguildid:
        if managementrole in [role.id for role in ctx.author.roles] or ownerrole in [role.id for role in ctx.author.roles]:
            return True
        else:
            return False
    else:
        return True

def member_is_verified(member: discord.Member):
    if verifiedrole in [role.id for role in member.roles]:
        return True
    else:
        return False

def member_is_admin(member: discord.Member):
    for role in member.roles:
        if role.id in staffroles:
            return True
    return False

def member_is_management(member: discord.Member):
    if managementrole in [role.id for role in member.roles] or ownerrole in [role.id for role in member.roles]:
        return True
    else:
        return False

def member_is_muted(member: discord.Member):
    if mutedrole in [role.id for role in member.roles]:
        return True
    else:
        return False
    