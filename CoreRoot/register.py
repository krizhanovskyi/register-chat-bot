import aiohttp


URL = 'http://127.0.0.1:8000/api/auth/register/'
headers = {'content-type': 'application/json; charset=UTF-8'}


async def register(body):
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, data=body, headers=headers) as response:
            msg = await response.text()
            if response.status == 201:
                return response.status
            else:
                return msg
