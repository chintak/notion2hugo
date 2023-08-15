import importlib
import tomllib
from importlib import resources
from typing import Any, Dict, Type

from notion2hugo.base import IConfig
from notion2hugo.runner import Runner, RunnerConfig
from notion2hugo.utils import get_logger

TConfig = Dict[str, Dict[str, Any]]
VALID_CONFIG_STRUCT: TConfig = {
    "runner_config": {
        "provider_config_cls": None,
        "formatter_config_cls": None,
        "exporter_config_cls": None,
    },
    "provider_config": {},
    "formatter_config": {},
    "exporter_config": {},
}


def import_and_load_config_cls(path: str) -> Type[IConfig]:
    module_path, cls_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    assert hasattr(
        module, cls_name
    ), f"Config class {cls_name} not found in module {module_path}"
    return getattr(module, cls_name)


def validate_and_load_config(resource_config_path: str) -> TConfig:
    # load package resource config.toml
    config = tomllib.loads(resources.read_text(__package__, resource_config_path))
    assert set(VALID_CONFIG_STRUCT.keys()).issubset(
        config.keys()
    ), f"Expected config.toml structure to be like {VALID_CONFIG_STRUCT}"
    assert set(VALID_CONFIG_STRUCT["runner_config"].keys()).issubset(
        config["runner_config"].keys()
    ), f"Expected config.toml structure to be like {VALID_CONFIG_STRUCT}"

    return config


def main():
    logger = get_logger(__package__)
    config = validate_and_load_config("config.toml")
    logger.info(f"Loading config: {config}")

    provider_config_cls = import_and_load_config_cls(
        config["runner_config"]["provider_config_cls"]
    )
    formatter_config_cls = import_and_load_config_cls(
        config["runner_config"]["formatter_config_cls"]
    )
    exporter_config_cls = import_and_load_config_cls(
        config["runner_config"]["exporter_config_cls"]
    )

    runner_config = RunnerConfig(
        provider_config=provider_config_cls(**config["provider_config"]),
        formatter_config=formatter_config_cls(**config["formatter_config"]),
        exporter_config=exporter_config_cls(**config["exporter_config"]),
    )
    logger.info(f"Runner config = {runner_config}")
    runner = Runner(config=runner_config)
    logger.info("Processing starting...")
    runner.run()
    logger.info("Processing complete.")


if __name__ == "__main__":
    main()
