from sqlalchemy import insert, select, func, text
from sqlalchemy.exc import OperationalError
from data.models.currencies import Currencies
import logging


class CurrenciesRep:
    def __init__(self, connection) -> None:
        self.connection = connection
    
    async def get_currency_id_by_name(self, name):
        async with self.connection.connect() as conn:
            result = await conn.execute(select(Currencies).where(Currencies.name == name))
            result = result.first()
            if not result:
                return result
            return result.id
    
    async def add_currencies(self, currency_info_names):
        try:
            async with self.connection.connect() as conn:
                async with conn.begin():
                    for name in currency_info_names:
                        await conn.execute(insert(Currencies).values(
                            name=name
                        ))
                    await conn.commit()
        except OperationalError as e:
            logging.error(f"Smth went wrong {e}")

    async def get_all_currencies(self):
        async with self.connection.connect() as conn:
            return await conn.execute(select(Currencies))
    
    async def get_currency_quantity(self):
        async with self.connection.connect() as conn:
            cursor = await conn.execute(text("SELECT COUNT(*) FROM currencies"))
            cursor = cursor.first()[0]
            return cursor
    
    async def get_currencies_page(self, start: int, end: int):
        async with self.connection.connect() as conn:
            return await conn.execute(select(Currencies).where(Currencies.id.between(start, end)))
