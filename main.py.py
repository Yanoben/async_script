import aiohttp
import asyncio
import hashlib
import os
from async_exit_stack import AsyncExitStack
from pathlib import Path

async def download_and_hash(session, file_path, url):
    async with session.get(url) as r:
        if r.status == 200:
            contents = await r.content.read()
            sha256 = hashlib.sha256(contents).hexdigest()
            return (file_path, sha256)

async def main():
    url = 'https://gitea.radium.group/radium/project-configuration.git'
    tmp_dir = Path('./tmp')
    await tmp_dir.mkdir(exist_ok=True)
    tasks = []
    async with AsyncExitStack() as stack:
        session = stack.enter_context(aiohttp.ClientSession())
        async with stack.enter_context(tmp_dir):
            async with session.head(url) as resp:
                # Get the list of files to download
                headers = resp.headers.get('Content-Disposition', '').split(';')
                for header in headers:
                    if header.strip().startswith('filename='):
                        filename = header[len('filename='):].strip('"')
                        file_path = tmp_dir / filename
                        tasks.append(asyncio.create_task(download_and_hash(session, file_path, url)))
        # Run the tasks concurrently
        results = await asyncio.gather(*tasks)
        # Write the results to a file
        with open('results.txt', 'w') as f:
            for result in results:
                f.write(f'{result[0]}: {result[1]}\n')

if __name__ == '__main__':
    asyncio.run(main())
