import os, yaml
from typing import Union

from depraved_bot.kinks import RequiredKink, OptionalKink

def load_config(path: Union[str, bytes, os.PathLike]) -> tuple[list, list]:
    '''Loads a config YAML file from the given path, extracts the relevant data, and returns them.'''
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    required_kinks = [RequiredKink(kink) for kink in config["kinks"]["required_kinks"]]
    optional_kinks = [OptionalKink(kink) for kink in config["kinks"]["optional_kinks"]]
    return required_kinks, optional_kinks