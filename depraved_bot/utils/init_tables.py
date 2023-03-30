from sqlalchemy import Engine, Table, MetaData, Column, BigInteger, String
from sqlalchemy.dialects.postgresql import ARRAY

def init_tables(engine: Engine, metadata: MetaData) -> tuple[Table, Table, Table]:
    '''Initialize tables in the PostgreSQL database.'''
    required_table = Table(
        "required_kinks",
        metadata,
        Column("name", String, primary_key=True),
        Column("id", BigInteger),
        autoload_with=engine,
    )
    optional_table = Table(
        "optional_kinks",
        metadata,
        Column("name", String, primary_key=True),
        Column("green", BigInteger),
        Column("yellow", BigInteger),
        Column("red", BigInteger),
        autoload_with=engine,
    )
    members_table = Table(
        "members",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("roles", ARRAY),
        autoload_with=engine,
    )

    return required_table, optional_table, members_table