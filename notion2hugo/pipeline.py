#!/usr/bin/python3

"""Defines the top level abstraction which encapsulates export logic."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional, Union

from notion_client import AsyncClient


@dataclass(frozen=True)
class BaseDatabaseConfig:
    database_id: int


@dataclass(frozen=True)
class NotionFilterConfig:
    key: str
    include: Optional[Union[Any, List[Any]]] = None
    exclude: Optional[Union[Any, List[Any]]] = None


@dataclass(frozen=True)
class NotionDatabaseConfig(BaseDatabaseConfig):
    filters: List[NotionFilterConfig]


@dataclass(frozen=True)
class BaseParserConfig:
    pass


@dataclass(frozen=True)
class BaseFormatterConfig:
    pass


@dataclass(frozen=True)
class BaseWriterConfig:
    def __init__(self):
        self.abc = 1


@dataclass(frozen=True)
class BasePipelineConfig:
    database_config: BaseDatabaseConfig
    parser_config: BaseParserConfig
    formatter_config: BaseFormatterConfig
    writer_config: BaseWriterConfig


class BasePipeline(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_parser(self, config: BaseParserConfig) -> BaseParser:
        return NotImplementedError
