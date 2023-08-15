#!/usr/bin/env python3

from abc import ABCMeta
from dataclasses import dataclass
from functools import wraps
from typing import Dict, Type

from notion2hugo.utils import get_logger

TConfigHash = int
_REGISTRY: Dict[TConfigHash, Type["IHandler"]] = {}


def register_handler(config):
    @wraps(config)
    def wrapper(cls):
        _REGISTRY[config.hash()] = cls
        return cls

    return wrapper


@dataclass(frozen=True)
class IConfig:
    @classmethod
    def hash(cls) -> TConfigHash:
        return hash(cls.__qualname__)

    def __eq__(self, another: object) -> bool:
        if hasattr(another, "hash"):
            return self.hash() == another.hash()
        return False


@register_handler(IConfig)
class IHandler(metaclass=ABCMeta):
    def __init__(self, config: IConfig):
        self.logger = get_logger(__package__)


class Factory(object):
    @classmethod
    def build_handler(cls, config: IConfig) -> IHandler:
        global _REGISTRY
        handler_cls = _REGISTRY.get(config.hash())
        if handler_cls:
            return handler_cls(config)
        raise ValueError(f"Unsupported config of type {type(config).__qualname__}")
