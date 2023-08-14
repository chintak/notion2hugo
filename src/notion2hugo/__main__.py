import importlib
import tomllib

from notion2hugo.runner import Runner, RunnerConfig


def main():
    # load package resource config.toml
    config = tomllib.loads(importlib.resources.read_text(__package__, "config.toml"))

    runner = Runner(config=RunnerConfig)
    runner.run()


if __name__ == "__main__":
    main()
