import aiohttp

headers = {'content-type': 'application/json; charset=UTF-8'}

async def register(body, url):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=body, headers=headers) as response:
            msg = await response.text()
            if response.status == 201:
                return response.status
            else:
                return msg
