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
    url = f'https://tryshort.in/api'
    api_key = "41d5dfab6c64a21e0e3e81b6eb3c947f28c7105c"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink
    
async def gplinks(link):
    url = f'https://earnfly.net/api'
    api_key = "daae6d5c8beace88e448b1059af2946df208b423"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink

async def adlinkfly(link):
    url = f'https://sharedisklinks.com/api'
    api_key = "fcd5336319ff60a848b4df69fd24664070d1691e"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink

async def urlshare(link):
    url = f'https://tnshort.net/api'
    api_key = "92a0a35b61d389ec15c093890edd7360fb39531b"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink

async def runurl(link):
    url = f'https://runurl.in/api'
    api_key = "53a50fec01bc1a0931fbe2b4c713bf051811b1ea"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink

async def thh(link):
    url = f'https://thh.aslink.in/api'
    api_key = "bd6f5d021a1c524512ebb40072962203a3abb7de"
    params = {'api': api_key, 'url': link, 'format': 'text'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True) as response:
                return await response.text()
    except Exception as e:
        shortlink = f"{url}?api={api_key}&url={link}&format=text"
        return shortlink
