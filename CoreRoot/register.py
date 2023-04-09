import aiohttp
from aiohttp import FormData

headers = {'content-type': 'application/json; charset=UTF-8'}

async def register(body, url):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=body, headers=headers) as response:
            msg = await response.text()
            if response.status == 201:
                return response.status
            else:
                return msg

async def upload_user_profile_photo(url, file_io_object, filename, user_id):
        formdata = FormData()
        formdata.add_field('file', file_io_object, filename=filename)
        formdata.add_field('user_id', user_id)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=formdata) as response:
                print(response.status)
                print(await response.text())