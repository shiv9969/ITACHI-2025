import aiohttp, asyncio
from database.config_db import mdb

async def shortlink(link):
    shortner = await mdb.get_configuration_value("shortner")
    if shortner is None or shortner == "shareus":
        return await shareus(link)
    elif shortner == "gplinks":
        return await gplinks(link)
    if shortner == "adlinkfly":
        return await adlinkfly(link)
    if shortner == "urlshare":
        return await urlshare(link)
    if shortner == "runurl":
        return await runurl(link)
    if shortner == "thh":
        return await thh(link)
    if shortner == "no_shortner":
        return link
        
async def shareus(link):
    url = f'https://adlinkfly.in/api'
    api_key = "728ac8e235b7da546190c8a97c73ddedcd8e27cf"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink
    
async def gplinks(link):
    url = f'https://adlinkfly.in/api'
    api_key = "728ac8e235b7da546190c8a97c73ddedcd8e27cf"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink

async def adlinkfly(link):
    url = f'https://adlinkfly.in/api'
    api_key = "728ac8e235b7da546190c8a97c73ddedcd8e27cf"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink

async def urlshare(link):
    url = f'https://adlinkfly.in/api'
    api_key = "728ac8e235b7da546190c8a97c73ddedcd8e27cf"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink

async def runurl(link):
    url = f'https://adlinkfly.in/api'
    api_key = "728ac8e235b7da546190c8a97c73ddedcd8e27cf"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink

async def thh(link):
    url = f'https://adlinkfly.in/api'
    api_key = "728ac8e235b7da546190c8a97c73ddedcd8e27cf"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink
