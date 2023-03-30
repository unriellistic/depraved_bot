import os, yaml
from typing import Union

from sqlalchemy import Engine, Table, select

from depraved_bot.structures.kinks import RequiredKink, OptionalKink

def load_config_from_yaml(path: Union[str, bytes, os.PathLike]) -> tuple[list, list]:
    '''Loads a config YAML file from the given path, extracts the relevant data, and returns them.'''
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    required_kinks = [RequiredKink.parse_obj(kink) for kink in config["kinks"]["required_kinks"]]
    optional_kinks = [OptionalKink.parse_obj(kink) for kink in config["kinks"]["optional_kinks"]]
    return required_kinks, optional_kinks

def load_config_from_sql(engine: Engine, table_required: Table, table_optional: Table) -> tuple[list, list]:
    '''Loads bot configuration data from a SQLAlchemy engine.'''
    required_kinks = []
    optional_kinks = []

    with engine.connect() as conn:
        # _mapping gives us the row in dict form, so we can pass it to pydantic parse_obj
        for kink in conn.execute(select(table_required)):
            required_kinks.append(RequiredKink.parse_obj(kink._mapping))
        for kink in conn.execute(select(table_optional)):
            optional_kinks.append(OptionalKink.parse_obj(kink._mapping))
    
    return required_kinks, optional_kinks