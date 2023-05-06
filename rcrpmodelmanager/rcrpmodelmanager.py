import discord
import aiomysql
import aiohttp
import aiofiles
import aiofiles.os
import re
import os
import json
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_list
from typing import Union
from redbot.core.bot import Red


class model_types():
    def __init__(self):
        self.model_type_ped = 0
        self.model_type_object = 1

    def get_model_range_for_type(self, modeltype: Union[str, int]):
        """Returns the valid range of model IDs for a specific type"""
        if (isinstance(modeltype, str) and modeltype.upper() == 'PED') or (isinstance(modeltype, int) and modeltype == self.model_type_ped):
            return 20000, 30000
        elif (isinstance(modeltype, str) and modeltype.upper() == 'OBJECT') or (isinstance(modeltype, int) and modeltype == self.model_type_object):
            return -30000, -1000
        else:
            return -1, -1

    def model_type_int(self, modeltype: str):
        """Returns the reference constant for model types that's used in the MySQL database/RCRP script"""
        modeltype = modeltype.upper()
        if modeltype == 'PED':
            return 0
        elif modeltype == 'OBJECT':
            return 1
        else:
            return -1

    def model_type_name(self, modeltype: int):
        """Returns the reference string for model types based on the constant used in the MySQL database/RCRP script"""
        if modeltype == 0:
            return 'PED'
        elif modeltype == 1:
            return 'OBJECT'
        else:
            return 'INVALID'

    async def is_valid_model(self, modelid: int):
        """Queries the MySQL database to see if a model ID exists"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT NULL FROM models WHERE modelid = %s", (modelid, ))
        rows = cursor.rowcount
        await cursor.close()
        sql.close()

        return rows != 0

    def is_valid_model_type(self, modeltype: str):
        """Checks if the supplied string matches a valid model type. Valid types are 'PED' or 'OBJECT'"""
        temp_type = modeltype.upper()
        if temp_type != 'PED' and temp_type != 'OBJECT':
            return False
        else:
            return True


class model_data():
    """Model data"""
    def __init__(self, data: dict = {}):
        if len(data) != 0:
            # resolve a model based on a dict from a mysql cursor
            self.model_id: int = data['modelid']
            self.reference_model: int = data['reference_model']
            self.dff_name: str = data['dff_name']
            self.txd_name: str = data['txd_name']
            self.model_type: str = model_types().model_type_name(data['modeltype'])
            self.model_path: str = data['folder']
        else:
            self.model_id: int = 0
            self.reference_model: int = 0
            self.dff_name: str = ""
            self.txd_name: str = ""
            self.model_type: str = ""
            self.model_path: str = ""


class RCRPModelManager(commands.Cog):
    """RCRP Model Manager"""
    def __init__(self, bot: Red):
        self.bot = bot
        self.models = {}  # dict for pending model data. key will be the model's ID
        self.model_urls = []  # list containing each URL that needs to used for downloading
        self.rcrp_model_path = "/home/rcrp/domains/cdn.redcountyrp.com/public_html/rcrp"  # path of RCRP models
        self.relay_channel_id = 776943930603470868

    async def send_relay_channel_message(self, message: str):
        rcrpguild = await self.bot.fetch_guild(93142223473905664)
        relaychannel = rcrpguild.get_channel(self.relay_channel_id)
        await relaychannel.send(message)

    async def validate_model_submission(self, modelid: int, dff_url: str, txd_url: str):
        if modelid in self.models:
            return f'Model ID {modelid} is already present in the pending models list.'

        if await model_types().is_valid_model(modelid):
            return f'The model {modelid} is already present on the server.'

        min, max = model_types().get_model_range_for_type(model_types().model_type_object)
        if modelid not in range(min, max):
            return f'Invalid object model ID. Please use a range of {min} to {max} for this type.'

        if dff_url.endswith('.dff') is False:
            return 'DFF URL does not seem to actually be a DFF file.'

        if txd_url.endswith('.txd') is False:
            return 'TXD URL does not seem to actually be a TXD file.'

    def strip_model_urls(self, dff_url: str, txd_url: str):
        dff_match = re.search('https://cdn.discordapp.com/attachments/[0-9]*/[0-9]*/', dff_url)
        if dff_match is None:
            return 'Invalid Discord URL formatting for DFF URL.', '', ''

        txd_match = re.search('https://cdn.discordapp.com/attachments/[0-9]*/[0-9]*/', txd_url)
        if txd_match is None:
            return 'Invalid Discord URL formatting for TXD URL.', '', ''

        txd_name = txd_url.replace(txd_match.group(), '')
        dff_name = dff_url.replace(dff_match.group(), '')
        return '', txd_name, dff_name

    @commands.group()
    @commands.is_owner()
    async def modelmanager(self, ctx):
        """Manage and add new custom models"""
        pass

    @modelmanager.command()
    @commands.is_owner()
    async def addobject(self, ctx: commands.Context, modelid: int, reference_id: int, folder: str, dff_url: str, txd_url: str):
        """Adds a new object model to the list of pending models"""
        error = await self.validate_model_submission(modelid, dff_url, txd_url)
        if error is not None:
            await ctx.send(error)
            return

        error, txd_name, dff_name = self.strip_model_urls(dff_url, txd_url)
        if len(error) != 0:
            await ctx.send(error)
            return

        # add model URLs to the list
        self.model_urls.append(dff_url)
        self.model_urls.append(txd_url)

        # assign pending model data, add it to dict
        model_info = model_data()
        model_info.model_id = modelid
        model_info.reference_model = reference_id
        model_info.dff_name = dff_name
        model_info.txd_name = txd_name
        model_info.model_type = model_types().model_type_name(model_types().model_type_object)
        model_info.model_path = f'objects/{folder}'
        self.models[modelid] = model_info
        await ctx.send(f'Model ID {modelid} has been added to the pending models list. Use !modelmanager finalize when you are ready to download the pending models to the server and add them in-game.')

    @modelmanager.command()
    @commands.is_owner()
    async def addped(self, ctx: commands.Context, modelid: int, reference_id: int, folder: str, dff_url: str, txd_url: str):
        """Adds a new model to the pending models list"""
        error = await self.validate_model_submission(modelid, dff_url, txd_url)
        if len(error) != 0:
            await ctx.send(error)
            return

        error, txd_name, dff_name = self.strip_model_urls(dff_url, txd_url)
        if len(error) != 0:
            await ctx.send(error)
            return

        # add model URLs to the list
        self.model_urls.append(dff_url)
        self.model_urls.append(txd_url)

        # assign pending model data, add it to dict
        model_info = model_data()
        model_info.model_id = modelid
        model_info.reference_model = reference_id
        model_info.dff_name = dff_name
        model_info.txd_name = txd_name
        model_info.model_type = model_types().model_type_name(model_types().model_type_ped)
        model_info.model_path = f'peds/{folder}'
        self.models[modelid] = model_info
        await ctx.send(f'Model ID {modelid} has been added to the pending models list. Use !modelmanager finalize when you are ready to download the pending models to the server and add them in-game.')

    @modelmanager.command()
    @commands.is_owner()
    async def removependingmodel(self, ctx: commands.Context, modelid: int):
        """Removes a model from the list of current pending models"""
        if len(self.models) == 0:
            await ctx.send('There are currently no pending models.')
            return

        if modelid not in self.models:
            await ctx.send('No pending model found with that ID.')
            return

        del self.models[modelid]
        await ctx.send(f'Model ID {modelid} has been removed from the pending models list.')

    @modelmanager.command()
    @commands.is_owner()
    async def deletemodel(self, ctx: commands.Context, modelid: int, deletefiles: bool):
        """Removes a custom model from database (and optionally, deletes the file itself) (RCRP restart required for full effect)"""
        if await model_types().is_valid_model(modelid) is False:
            await ctx.send(f'{modelid} is not a model ID that is used on the server.')
            return

        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)

        if deletefiles:
            await cursor.execute("SELECT * FROM models WHERE modelid = %s", (modelid, ))
            data = await cursor.fetchone()
            modelfolder = data['folder']
            model_dff = data['dff_name']
            model_txd = data['txd_name']
            model_path = f'{self.rcrp_model_path}/{modelfolder}'

            if os.path.isfile(f'{model_path}/{model_dff}'):
                os.remove(f'{model_path}/{model_dff}')
            if os.path.isfile(f'{model_path}/{model_txd}'):
                os.remove(f'{model_path}/{model_txd}')

            remaining_files = os.listdir(model_path)
            if len(remaining_files) == 0:  # folder is empty, delete it
                os.rmdir(model_path)

        await cursor.execute("DELETE FROM models WHERE modelid = %s", (modelid, ))
        await cursor.close()
        sql.close()

        await ctx.send(f'Model {modelid} has been deleted from the MySQL database and will not be loaded on the next server restart.')

    @modelmanager.command()
    @commands.is_owner()
    async def pending(self, ctx: commands.Context, modelid: int):
        """Views the information of a pending model that has not been sent to the server yet"""
        if len(self.models) == 0:
            await ctx.send('There are currently no pending models.')
            return

        if modelid not in self.models:
            await ctx.send('No pending model found with that ID.')
            return

        model_info: model_data = self.models[modelid]
        embed = discord.Embed(title=f'Pending Model Information ({modelid})', color=0xe74c3c)
        embed.add_field(name='Reference ID', value=model_info.reference_model, inline=False)
        embed.add_field(name='TXD File Name', value=model_info.txd_name, inline=False)
        embed.add_field(name='DFF File Name', value=model_info.dff_name, inline=False)
        embed.add_field(name='Model Type', value=model_info.model_type, inline=False)
        embed.add_field(name='Model Path', value=model_info.model_path, inline=False)
        await ctx.send(embed=embed)

    @modelmanager.command(aliases=['info', 'modelinfo'])
    @commands.is_owner()
    async def fetch(self, ctx: commands.Context, modelid: int):
        """Retrieves information about an existing model from the MySQL database"""
        if await model_types().is_valid_model(modelid) is False:
            await ctx.send(f'{modelid} is not a valid model ID used on the server.')
            return

        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT * FROM models WHERE modelid = %s", (modelid, ))
        results = await cursor.fetchone()
        model = model_data(results)
        await cursor.close()
        sql.close()

        url_path = model.model_path.replace(' ', '%20')
        embed = discord.Embed(title=f'Model Information ({modelid})', color=0xe74c3c)
        embed.add_field(name='TXD', value=model.txd_name, inline=False)
        embed.add_field(name='DFF', value=model.dff_name, inline=False)
        embed.add_field(name='Model Type', value=model.model_type, inline=False)
        embed.add_field(name='Model Path', value=model.model_path, inline=False)
        embed.add_field(name='DFF URL', value=f"https://redcountyrp.com/cdn/rcrp/{url_path}/{model.dff_name}", inline=False)
        embed.add_field(name='TXD URL', value=f"https://redcountyrp.com/cdn/rcrp/{url_path}/{model.txd_name}", inline=False)
        if model_types().model_type_int(model.model_type) == model_types().model_type_ped:
            embed.add_field(name='Artconfig', value=f'AddCharModel({model.reference_model}, {model.model_id}, "{model.dff_name}", "{model.txd_name}");')
        else:
            embed.add_field(name='Artconfig', value=f'AddSimpleModel(-1, {model.reference_model}, {model.model_id}, "{model.dff_name}", "{model.txd_name}");')
        await ctx.send(embed=embed)

    @modelmanager.command()
    @commands.is_owner()
    async def search(self, ctx: commands.Context, search: str):
        """Searches the database to find models of the specified type with the search term in their DFF name"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)

        await cursor.execute("SELECT * FROM models WHERE dff_name LIKE %s", (('%' + search + '%'), ))
        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send('Could not find a model of that type based on your search term.')
            return

        data = await cursor.fetchall()
        await cursor.close()
        sql.close()

        embed = discord.Embed(title='Search Results', color=0xe74c3c)
        for model in data:
            embed.add_field(name='Model ID', value=model['modelid'], inline=True)
            embed.add_field(name='DFF Name', value=model['dff_name'], inline=True)
            embed.add_field(name='TXD Name', value=model['txd_name'], inline=True)
        await ctx.send(embed=embed)

    @modelmanager.command()
    @commands.is_owner()
    async def finalize(self, ctx: commands.Context):
        """Downloads all pending models and sends a signal to the RCRP gamemode to check for models that are currently not loaded"""
        if len(self.models) == 0:
            await ctx.send('There are currently no pending models.')
            return

        # list of inserted model IDs to be sent to the RCRP game server
        model_id_list = []

        # convert models dict to a list for easier iterating, then clear the dict
        model_list = list(self.models.values())
        model_count = len(model_list)
        self.models.clear()

        await ctx.send(f'{model_count} {"models" if model_count != 1 else "model"} will now be added to RCRP.')

        # remove any duplicate URLs from the list (for objects that may share the same txd or dff)
        self.model_urls = list(dict.fromkeys(self.model_urls))
        url_count = len(self.model_urls)

        # download!
        tempfolder = f'{self.rcrp_model_path}/temp'
        await ctx.send(f'Beginning the download of the {url_count} necessary {"files" if url_count != 1 else "file"}.')
        if os.path.exists(tempfolder) is False:
            await aiofiles.os.mkdir(tempfolder)

        async with ctx.typing():
            for url in self.model_urls:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            file_match = re.search('https://cdn.discordapp.com/attachments/[0-9]*/[0-9]*/', url)
                            filename = url.replace(file_match.group(), '')
                            data = await response.read()
                            async with aiofiles.open(f'{tempfolder}/{filename}', 'wb') as file:
                                await file.write(data)
            await ctx.send(f'Finished downloading {url_count} {"files" if url_count != 1 else "file"}.')
        self.model_urls.clear()

        # insert the models into the MySQL database and then move them to the correct directories
        await ctx.send('Inserting new models into the MySQL database and moving them to their correct folders.')
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        async with ctx.typing():
            for model in model_list:
                model_id_list.append(f'{model.model_id}')
                await cursor.execute("INSERT INTO models (modelid, reference_model, modeltype, dff_name, txd_name, folder) VALUES (%s, %s, %s, %s, %s, %s)", (model.model_id, model.reference_model, model_types().model_type_int(model.model_type), model.dff_name, model.txd_name, model.model_path))
                destinationfolder = f'{self.rcrp_model_path}/{model.model_path}'

                if os.path.exists(destinationfolder) is False:
                    await aiofiles.os.mkdir(destinationfolder)

                if os.path.isfile(f'{tempfolder}/{model.dff_name}') and os.path.isfile(f'{destinationfolder}/{model.dff_name}') is False:
                    await aiofiles.os.rename(f'{tempfolder}/{model.dff_name}', f'{destinationfolder}/{model.dff_name}')

                if os.path.isfile(f'{tempfolder}/{model.txd_name}') and os.path.isfile(f'{destinationfolder}/{model.txd_name}') is False:
                    await aiofiles.os.rename(f'{tempfolder}/{model.txd_name}', f'{destinationfolder}/{model.txd_name}')

        await cursor.close()
        sql.close()

        # send a message to the rcrp game server so it'll load the models
        message = humanize_list(model_id_list)
        message = message.replace(', and', ',')
        rcrp_message = {
            "callback": "LoadCustomModels",
            "models": message
        }
        await self.send_relay_channel_message(json.dumps(rcrp_message))
        await ctx.send(f'{model_count} {"models" if model_count != 1 else "model"} has been successfully downloaded and put in their appropriate directories. The RCRP game server has been instructed to check for new models.')

        # remove the temporary directory
        temp_files = os.listdir(tempfolder)
        if len(temp_files) != 0:
            for file in temp_files:
                await aiofiles.os.remove(f'{tempfolder}/{file}')
        await aiofiles.os.rmdir(f'{tempfolder}')
