import pytest
import hashlib
from pathlib import Path

@pytest.fixture
def tmp_dir(tmp_path):
    return Path(tmp_path)

@pytest.mark.asyncio
async def test_download_and_hash(tmp_dir):
    from my_script import download_and_hash
    async with aiohttp.ClientSession() as session:
        url = 'https://gitea.radium.group/radium/project-configuration.git'
        file_path = tmp_dir / 'README.md'
        sha256_expected = 'bf8b453329ec76f9e920e501b78dcf1a547c85eaf521529da100c59de788305e'
        sha256_actual = await download_and_hash(session, file_path, url)
        assert sha256_actual == (file_path, sha256_expected)

def test_main(tmp_dir, monkeypatch):
    from my_script import main
    import asyncio
    results_path = tmp_dir / 'results.txt'
    loop = asyncio.get_event_loop()
    # Mock the AsyncExitStack context
    async with AsyncExitStack() as stack:
        stack.enter_context(monkeypatch.context())
        stack.enter_context(tmp_dir)
        # Mock the response object for the HEAD request
        async def mock_head_request(url):
            class MockResponse:
                headers = {'Content-Disposition': 'attachment; filename=README.md'}
                async def __aenter__(self):
                    return self
                async def __aexit__(self, exc_type, exc_value, traceback):
                    pass
            return MockResponse()
        with monkeypatch.context() as m:
            m.setattr(aiohttp.ClientSession,'head', mock_head_request)
            loop.run_until_complete(main())
    # Check that the results file was created and has the correct content
    assert results_path.exists()
    with results_path.open('r') as f:
        contents = f.read()
        assert 'README.md: bf8b453329ec76f9e920e501b78dcf1a547c85eaf521529da100c59de788305e' in contents
