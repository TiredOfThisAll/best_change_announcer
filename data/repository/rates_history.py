from sqlalchemy import insert, select, func

from data.models.rates_history import RatesHistory


class RatesHistoryRep:
    def __init__(self, connection) -> None:
        self.connection = connection
    
    async def add_rates(self, conversion_info: dict):
        async with self.connection.connect() as conn:
            async with conn.begin():
                await conn.execute(insert(RatesHistory).values(
                    conversion_id=conversion_info["conversion_id"],
                    rate=conversion_info["rate"],
                    ascending=conversion_info["ascending"],
                    date=conversion_info["date"]
                ))
                await conn.commit()
    
    async def get_rates_by_id_for_period(self, conversion_id, start, end):
        async with self.connection.connect() as conn:
            return await conn.execute(select(RatesHistory).where(
                RatesHistory.conversion_id == conversion_id & RatesHistory.date.between(start, end)
            ))
    
    async def get_rates_by_id(self, conversion_id):
        async with self.connection.connect() as conn:
            return await conn.execute(select(RatesHistory).where(
                RatesHistory.conversion_id == conversion_id
            ))
    
    async def get_max_rate_by_conv_id(self, conversion_id):
        async with self.connection.connect() as conn:
            return await conn.execute(select(func.max(RatesHistory.rate)).where(
                RatesHistory.conversion_id == conversion_id
            ))
    
    async def get_max_rate_by_conv_id_for_period(self, conversion_id, start, end):
        async with self.connection.connect() as conn:
            return await conn.execute(select(func.max(RatesHistory.rate)).where(
                RatesHistory.conversion_id == conversion_id & RatesHistory.date.between(start, end)
            ))


    async def get_all_rates(self):
        async with self.connection.connect() as conn:
            return await conn.execute(select(RatesHistory))
