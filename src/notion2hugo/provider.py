#!/usr/bin/env python3

"""Defines the top level abstraction which encapsulates export logic."""
import asyncio
from dataclasses import asdict, dataclass, fields
from pprint import pformat
from typing import Any, AsyncIterator, Dict, List

from notion_client import AsyncClient
from notion_client.helpers import async_iterate_paginated_api

from notion2hugo import NOTION_TOKEN
from notion2hugo.base import (
    BaseProvider,
    BaseProviderConfig,
    Blob,
    BlobType,
    PageContent,
    register_handler,
)
from notion2hugo.utils import get_logger


@dataclass(frozen=True)
class NotionPageMetadata:
    archived: bool
    id: str
    last_edited_time: str
    parent: Dict[str, str]
    properties: Dict[str, Any]
    url: str

    @classmethod
    def init(cls, **kwargs) -> "NotionPageMetadata":
        vals = {}
        for field in fields(cls):
            assert field.name in kwargs, f"Missing expected field {field.name}"
            vals[field.name] = kwargs[field.name]
        return NotionPageMetadata(**vals)


@dataclass(frozen=True)
class NotionBlockData:
    id: str
    content: Dict[str, Any]
    type: BlobType


class NotionBlockParser:
    @classmethod
    def parse(cls, blocks: List[NotionBlockData]) -> Blob:
        logger = get_logger(__name__)
        assert blocks, "Expected at least 1 block in order to parse"
        blob_type = blocks[0].type
        id = blocks[0].id
        # TODO: add parsing logic
        content = ""
        for block in blocks:
            content = ""
            if len(blocks) > 1:
                logger.warning(pformat(block.content))
        return Blob(type=blob_type, content=content, id=id)


@dataclass(frozen=True)
class NotionProviderConfig(BaseProviderConfig):
    database_id: str
    filter: Dict[str, Any]


@register_handler(NotionProviderConfig)
class NotionProvider(BaseProvider):
    def __init__(self, config: NotionProviderConfig):
        super(NotionProvider, self).__init__(config)
        self.config: NotionProviderConfig = config
        self.client = AsyncClient(auth=NOTION_TOKEN)

    async def async_fetch_pages_from_db(self) -> List[NotionPageMetadata]:
        # fetch all available pages (metadata) from db
        page_metadatas: List[NotionPageMetadata] = []
        async for responses in async_iterate_paginated_api(
            self.client.databases.query, **asdict(self.config)
        ):
            for resp in responses:
                assert isinstance(resp, dict), resp
                if resp.get("object") == "page":
                    page_metadatas.append(NotionPageMetadata.init(**resp))
        return page_metadatas

    async def async_fetch_and_parse_page_content(
        self, metadata: NotionPageMetadata
    ) -> PageContent:
        blobs: List[Blob] = []
        # fetch corresponding page content
        section = []
        async for blocks in async_iterate_paginated_api(
            self.client.blocks.children.list,
            block_id=metadata.id,
            page_size=100,
        ):
            for block in blocks:
                section.append(
                    NotionBlockData(
                        id=block["id"],
                        content=block[block["type"]],
                        type=BlobType(block["type"]),
                    )
                )
                if not block["has_children"]:
                    blobs.append(NotionBlockParser.parse(section))
                    section.clear()

        return PageContent(id=metadata.id, blobs=blobs, properties={})

    async def async_iterate(self) -> AsyncIterator[PageContent]:
        self.logger.info("Querying Notion db")
        page_metadatas = await self.async_fetch_pages_from_db()

        self.logger.info(f"Notion db returned {len(page_metadatas)} pages.")

        for page in asyncio.as_completed(
            [
                self.async_fetch_and_parse_page_content(metadata)
                for metadata in page_metadatas
            ]
        ):
            yield await page

        self.logger.info("Completed retrieving all pages from db.")
