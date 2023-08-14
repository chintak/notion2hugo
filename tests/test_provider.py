#!/usr/bin/env python3


import pytest

from notion2hugo import NOTION_DATABASE_ID
from notion2hugo.provider import NotionProvider, NotionProviderConfig


class TestNotionProvider:
    @pytest.mark.asyncio
    async def test_provider(self):
        config = NotionProviderConfig(
            database_id=NOTION_DATABASE_ID,
            filter={
                "property": "# Status",
                "status": {
                    "does_not_equal": "Not Started",
                },
            },
        )
        provider = NotionProvider(config)
        result = []
        async for page in provider.async_iterate():
            result.append(page)
        assert len(result) == 3
