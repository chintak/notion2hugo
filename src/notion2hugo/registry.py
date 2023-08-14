#!/usr/bin/env python3

from abc import ABCMeta
from functools import wraps
from typing import Dict, Type

from notion2hugo.utils import get_logger

TConfigHash = int
_REGISTRY: Dict[TConfigHash, Type["IHandler"]] = {}


def register_handler(config):
    @wraps(config)
    def wrapper(cls):
        _REGISTRY[hash(config)] = cls
        return cls

    return wrapper


class IConfig(metaclass=ABCMeta):
    def __hash__(self) -> TConfigHash:
        return hash(type(self))

    def __eq__(self, another: object) -> bool:
        return hash(self) == hash(another)


@register_handler(IConfig)
class IHandler(metaclass=ABCMeta):
    def __init__(self, config: IConfig):
        self.logger = get_logger(type(self).__qualname__)


class Factory(object):
    @classmethod
    def build_handler(cls, config: IConfig) -> IHandler:
        global _REGISTRY
        handler_cls = _REGISTRY.get(hash(config))
        if handler_cls:
            return handler_cls(config)
        raise ValueError(f"Unsupported config of type {type(config).__qualname__}")
