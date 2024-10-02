from sqlalchemy import insert, select
from sqlalchemy.exc import OperationalError
from data.models.subscriptions import Subscriptions
from data.models.users import Users
from data.models.tracked_conversions import TrackedConversions
from data.models.currencies import Currencies
from sqlalchemy.orm import aliased
import asyncio

from data.data_access.create_connection import create_connection
import logging

class SubscriptionsRep:
    def __init__(self, connection) -> None:
        self.connection = connection
    
    async def add_subscription(self, user_id, conversion_id):
        async with self.connection.connect() as conn:
            await conn.execute(insert(Subscriptions).values(
                user_id=user_id,
                tracked_conversions_id=conversion_id
            ))
            await conn.commit()
    
    async def get_all_subscriptions(self):
        async with self.connection.connect() as conn:
            return await conn.execute(select(Subscriptions))
    
    async def get_subscription_info_by_conversion_id(self, conversion_id):
        async with self.connection.connect() as conn:
            from_currency = aliased(Currencies)
            to_currency = aliased(Currencies)
            stmt = select(
                Users.chat_id,
                from_currency.name.label("from_currency_name"),
                to_currency.name.label("to_currency_name")).join(
                Subscriptions, Subscriptions.user_id == Users.id
            ).join(
                TrackedConversions, TrackedConversions.id == Subscriptions.tracked_conversions_id
            ).join(
                from_currency, TrackedConversions.from_currency_id == from_currency.id
            ).join(
                to_currency, TrackedConversions.to_currency_id == to_currency.id
            ).where(
                TrackedConversions.id == conversion_id
            )

            result = await conn.execute(stmt)
            return result
