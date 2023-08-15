#!/usr/bin/env python3

import asyncio
import logging
from dataclasses import dataclass

from notion2hugo.base import (
    BaseExporter,
    BaseExporterConfig,
    BaseFormatter,
    BaseFormatterConfig,
    BaseProvider,
    BaseProviderConfig,
)
from notion2hugo.registry import Factory
from notion2hugo.utils import get_logger


@dataclass(frozen=True)
class RunnerConfig:
    provider_config: BaseProviderConfig
    formatter_config: BaseFormatterConfig
    exporter_config: BaseExporterConfig


class Runner(object):
    def __init__(self, config: RunnerConfig):
        self.logger = get_logger(__package__, logging.INFO)

        self.provider = Factory.build_handler(config.provider_config)
        self.formatter = Factory.build_handler(config.formatter_config)
        self.exporter = Factory.build_handler(config.exporter_config)

    async def async_run(self) -> None:
        assert isinstance(self.provider, BaseProvider)
        assert isinstance(self.formatter, BaseFormatter)
        assert isinstance(self.exporter, BaseExporter)

        self.logger.info(f"Processing {type(self.provider).__qualname__}.")
        async for page_content in self.provider.async_iterate():
            self.logger.info(f"Got 1 page from provider, id = {page_content.id}")

            self.logger.info(f"Processing {type(self.formatter).__qualname__}.")
            formatted_post = await self.formatter.async_process(page_content)

            self.logger.info(f"Processing {type(self.exporter).__qualname__}.")
            await self.exporter.async_process(formatted_post)
        self.logger.info("All pages processed.")

    def run(self) -> None:
        asyncio.run(self.async_run())
