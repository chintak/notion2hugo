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
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import AsyncIterator, List, Optional

from notion2hugo.registry import IConfig, IHandler, register_handler

Properties = MutableMapping[str, str | int | bool | List[str]]


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
    TABLE_ROW = "table_row"
    TO_DO = "to_do"


@dataclass(frozen=True)
class ContentWithAnnotation:
    plain_text: Optional[str] = None
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"
    href: Optional[str] = None
    is_equation: bool = False
    is_toggleable: bool = False
    is_caption: bool = False
    highlight: bool = field(init=False, default=False)

    def __post_init__(self):
        object.__setattr__(self, "highlight", self.color != "default")


@dataclass(frozen=True)
class Blob:
    id: str
    rich_text: List[ContentWithAnnotation]
    type: BlobType
    children: Optional[List["Blob"]]
    file: Optional[str]
    language: Optional[str]
    table_width: Optional[int]
    table_cells: Optional[List[List[ContentWithAnnotation]]]
    is_checked: Optional[bool]  # todo item


@dataclass(frozen=True)
class PageContent:
    blobs: List[Blob]
    id: str
    properties: Properties
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
