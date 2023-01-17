import aiohttp
import asyncio
import pytest


async def logs(cont, name):
    conn = aiohttp.UnixConnector(path='/var/run/docker.sock')
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(f"http://localhost/containers/{cont}/logs?follow=1&stdout=1") as resp:
            async for line in resp.content:
                print(name, line)

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def create_container():
    conn = aiohttp.UnixConnector(path='/var/run/docker.sock')
    async with aiohttp.ClientSession(connector=conn) as session1:
        async with session1.post(f"http://localhost/containers/create",
                                 json={"image": "nginx"},
                                 headers={'Content-Type': 'application/json'}) as resp:
            response = await resp.json()
            cont = response["Id"]
        await session1.post(f"http://localhost/containers/{cont}/start")

    yield cont

    conn2 = aiohttp.UnixConnector(path='/var/run/docker.sock')
    async with aiohttp.ClientSession(connector=conn2) as session:
        await session.post(f"http://localhost/containers/{cont}/stop")
        await session.delete(f"http://localhost/containers/{cont}")


async def test_logs(capsys, create_container):
    name = 'tmp'

    cont = create_container

    expected = []
    conn1 = aiohttp.UnixConnector(path='/var/run/docker.sock')
    timeout = aiohttp.ClientTimeout(total=1)
    try:
        async with aiohttp.ClientSession(connector=conn1, timeout=timeout) as session:
            async with session.get(f"http://localhost/containers/{cont}/logs?follow=1&stdout=1") as resp:
                async for line in resp.content:
                    expected.append(f'{name} {line}')
    except asyncio.exceptions.TimeoutError:
        ...

    task = asyncio.create_task(logs(cont, name))
    await asyncio.sleep(2)
    task.cancel()
    captured = capsys.readouterr()
    captured = captured.out.split('\n')

    assert captured[:-1] == expected
