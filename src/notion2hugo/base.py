""" Defines the base classes for all the objects in the system.
The main abstractions in the system are described below.

PageContent (dataclass)
-------------
- Data format type used to represent post content in a standard way.
- This struct is used to transfer data across components.

Provider (class)
--------
- Input: ProviderConfig
- Output: PageContent
- Interface with database/file system
- Fetch and read files
- Parse file content and output.

Formatter (class)
---------
- Input: PageContent (from Provider)
- Output: PageContent
- Consumes PageContent produces by the Provider.
- Modifies/transforms it appropriately and outputs it.

Exporter (class)
--------
- Input: PageContent (from Formatter), ExporterConfig
- Output: to DB/file system
- Consumes content from Formatter and writes the content to db or file system.

Runner
--------
- Input: RunnerConfig
- Abstraction used to encapsulate the task of init various components in the
  Runner, specifying the glue code of chaining the components together and
  running everything.

Provider --produces--> PageContent --consumed_by--> Formatter --produces-->
    PageContent --consumed_by--> Exporter
"""

from abc import abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import AsyncIterator, Dict, List, Optional, Union

from notion2hugo.registry import IConfig, IHandler, register_handler


class BlobType(StrEnum):
    BULLETED_LIST_ITEM = "bulleted_list_item"
    CODE = "code"
    DIVIDER = "divider"
    EQUATION = "equation"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    IMAGE = "image"
    NEWLINE = "newline"  # default
    NUMBERED_LIST_ITEM = "numbered_list_item"
    PARAGRAPH = "paragraph"
    QUOTE = "quote"
    TABLE = "table"


@dataclass(frozen=True)
class Content:
    text: str
    href: Optional[str]


@dataclass(frozen=True)
class Blob:
    content: str
    id: str
    type: BlobType


@dataclass(frozen=True)
class PageContent:
    blobs: List[Blob]
    id: str
    properties: Dict[str, Union[str, bool, int]]
    footer: Optional[Blob] = None
    header: Optional[Blob] = None


@dataclass(frozen=True)
class BaseProviderConfig(IConfig):
    pass


@register_handler(BaseProviderConfig)
class BaseProvider(IHandler):
    @abstractmethod
    def async_iterate(self) -> AsyncIterator[PageContent]:
        ...


@dataclass(frozen=True)
class BaseFormatterConfig(IConfig):
    pass


@register_handler(BaseFormatterConfig)
class BaseFormatter(IHandler):
    @abstractmethod
    async def async_process(self, content: PageContent) -> PageContent:
        ...


@dataclass(frozen=True)
class BaseExporterConfig(IConfig):
    pass


@register_handler(BaseExporterConfig)
class BaseExporter(IHandler):
    @abstractmethod
    async def async_process(self, content: PageContent) -> None:
        ...
