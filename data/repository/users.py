from sqlalchemy import insert, select
from sqlalchemy.exc import OperationalError
from data.models.users import Users
import logging

class UsersRep:
    def __init__(self, connection) -> None:
        self.connection = connection
    
    async def add_user(self, telegram_user_id, username, chat_id):
        async with self.connection.connect() as conn:
            await conn.execute(insert(Users).values(
                telegram_user_id=telegram_user_id,
                username=username,
                chat_id=chat_id
            ))
            await conn.commit()
    
    async def get_all_users(self):
        async with self.connection.connect() as conn:
            return await conn.execute(select(Users))
    
    async def get_user_by_user_id(self, user_id):
        async with self.connection.connect() as conn:
            user = await conn.execute(select(Users).where(Users.telegram_user_id == user_id))
            return user.first()
