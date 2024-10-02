from sqlalchemy import insert, select, func
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncEngine


from data.models.tracked_conversions import TrackedConversions
from data.models.currencies import Currencies


class TrackedConversionsRep:
    def __init__(self, connection: AsyncEngine) -> None:
        self.connection = connection

    async def add_currencies_pair(self, from_curr, to_curr):
        async with self.connection.connect() as conn:
            await conn.execute(insert(TrackedConversions).values(
                from_currency_id=from_curr,
                to_currency_id=to_curr
            ))
            await conn.commit()

    async def get_page(self, start, end):
        async with self.connection.connect() as conn:
            from_currency = aliased(Currencies)
            to_currency = aliased(Currencies)

            stmt = (
                select(
                    TrackedConversions.id,
                    to_currency.name.label('to_currency_name'),
                    from_currency.name.label('from_currency_name')
                )
                .select_from(
                    TrackedConversions
                ).join(
                        to_currency,
                        TrackedConversions.to_currency_id == to_currency.id
                ).join(
                    from_currency,
                    TrackedConversions.from_currency_id == from_currency.id
                ).where(TrackedConversions.id.between(start, end))
            )

            result = await conn.execute(stmt)
            rows = result.all()
            return rows

    async def get_conversions_quantity(self):
        async with self.connection.connect() as conn:
            result = await conn.execute(select(func.count()).select_from(TrackedConversions))
            return result.scalar()
    
    async def get_conversion_by_id(self, id):
        async with self.connection.connect() as conn:
            from_currency = aliased(Currencies)
            to_currency = aliased(Currencies)

            stmt = (
                select(
                    TrackedConversions.id,
                    to_currency.name.label('to_currency_name'),
                    from_currency.name.label('from_currency_name')
                )
                .select_from(
                    TrackedConversions
                ).join(
                        to_currency,
                        TrackedConversions.to_currency_id == to_currency.id
                ).join(
                    from_currency,
                    TrackedConversions.from_currency_id == from_currency.id
                ).where(
                    TrackedConversions.id == id
                )
            )

            result = await conn.execute(stmt)
            return result.first()
    
    async def get_all_conversions_with_ids(self):
        async with self.connection.connect() as conn:
            return await conn.execute(select(TrackedConversions))
    
    async def get_all_conversions_with_names(self):
        async with self.connection.connect() as conn:
            from_currency = aliased(Currencies)
            to_currency = aliased(Currencies)

            stmt = (
                select(
                    TrackedConversions.id,
                    to_currency.name.label('to_currency_name'),
                    from_currency.name.label('from_currency_name')
                )
                .select_from(
                    TrackedConversions
                ).join(
                        to_currency,
                        TrackedConversions.to_currency_id == to_currency.id
                ).join(
                    from_currency,
                    TrackedConversions.from_currency_id == from_currency.id
                )
            )

            result = await conn.execute(stmt)
            return result
