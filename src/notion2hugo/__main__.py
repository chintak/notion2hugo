import argparse
import importlib
import logging
import tomllib
from typing import Any, Dict, TextIO, Type

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


def validate_and_load_config(resource_config_file: TextIO) -> TConfig:
    # load package resource config.toml
    config = tomllib.loads(resource_config_file.read())
    if not resource_config_file.closed:
        resource_config_file.close()
    assert set(VALID_CONFIG_STRUCT.keys()).issubset(
        config.keys()
    ), f"Expected config.toml structure to be like {VALID_CONFIG_STRUCT}"
    assert set(VALID_CONFIG_STRUCT["runner_config"].keys()).issubset(
        config["runner_config"].keys()
    ), f"Expected config.toml structure to be like {VALID_CONFIG_STRUCT}"

    return config


def parse_input_args():
    readme = """
    Notion2Hugo: Export content written in Notion to markdown,
    compatible for [Hugo](https://gohugo.io/) blog.
    See the README file for more information.
    """
    parser = argparse.ArgumentParser(description=readme)
    parser.add_argument(
        "config_path",
        type=open,
        help="Specify path to config.toml. "
        "Clone `src/notion2hugo/config.sample.toml` with custom settings.",
    )
    return parser.parse_args()


def main():
    args = parse_input_args()
    config = validate_and_load_config(args.config_path)
    provider_config_cls = import_and_load_config_cls(
        config["runner_config"]["provider_config_cls"]
    )
    formatter_config_cls = import_and_load_config_cls(
        config["runner_config"]["formatter_config_cls"]
    )
    exporter_config_cls = import_and_load_config_cls(
        config["runner_config"]["exporter_config_cls"]
    )

    logger = get_logger(
        __package__,
        level=getattr(
            logging, config.get("logging", {"set_log_level": "INFO"})["set_log_level"]
        ),
    )
    runner_config = RunnerConfig(
        provider_config=provider_config_cls(**config["provider_config"]),
        formatter_config=formatter_config_cls(**config["formatter_config"]),
        exporter_config=exporter_config_cls(**config["exporter_config"]),
    )
    logger.info(f"Runner config = {runner_config}")
    runner = Runner(config=runner_config)
    runner.run()


if __name__ == "__main__":
    main()
