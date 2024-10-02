from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


def create_connection(connection_str) -> AsyncEngine:
    engine = create_async_engine(
        connection_str
    )
    return engine
