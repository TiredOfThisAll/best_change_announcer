import asyncio
import logging
import sys
import threading
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from parser import extract_html_content, craft_link, parse_currencies_from_html, parse_best_rate
from keyboard import create_currencies_markup, create_conversions_markup
from callbacks import FromRateCallback, ToRateCallback, PaginationCallback, SubscribeCallback

from data.data_access.create_connection import create_connection
from data.data_access.create_schema import create_schema

from data.repository.rates_history import RatesHistoryRep
from data.repository.currencies import CurrenciesRep
from data.repository.tracked_conversions import TrackedConversionsRep
from data.repository.users import UsersRep
from data.repository.subscriptions import SubscriptionsRep

PAGE_SIZE = 10

tracked_conversions = []

website_url = "https://www.bestchange.com/"

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6589616173:AAFK9XjL9eYb_lZEgM8IJ5rQcV1mK1l4Fiw"

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()

sqlite_connection = create_connection("sqlite+aiosqlite:///test.db")

asyncio.run(create_schema(sqlite_connection))

rates_repository = RatesHistoryRep(sqlite_connection)
currencies_repository = CurrenciesRep(sqlite_connection)
tracked_conversions_repository = TrackedConversionsRep(sqlite_connection)
users_repository = UsersRep(sqlite_connection)
subscriptions_repository = SubscriptionsRep(sqlite_connection)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("list"))
async def command_list_handler(message: Message) -> None:
    currencies = await currencies_repository.get_all_currencies()

    chat_id = message.chat.id

    max_message_len = 1000
    message_len_counter = 0
    response = []

    for currency in currencies:
        row = f"{currency.id}. {currency.name}"
        if len(row) + message_len_counter > max_message_len:
            await message.bot.send_message(chat_id, "```\n" + "\n".join(response) + "\n```", parse_mode="Markdown")
            await asyncio.sleep(0.5)
            response.clear()
            message_len_counter = 0
            response.append(row)
        else:
            response.append(row)

        message_len_counter += len(row)

    await message.bot.send_message(chat_id, "```\n" + "\n".join(response) + "\n```", parse_mode="Markdown")


@dp.message(Command("track"))
async def command_track_rate_handler(message: Message) -> None:
    reply_markup = await create_currencies_markup(
        currencies_repository=currencies_repository,
        page_size=PAGE_SIZE,
        command="track"
    )
    await message.answer(
        text="Choose currency that you wanna give",
        reply_markup=reply_markup
    )


@dp.message(Command("subscribe"))
async def command_subscribe_handler(message: Message) -> None:
    reply_markup = await create_conversions_markup(
        conversions_repository=tracked_conversions_repository,
        page_size=PAGE_SIZE,
        command="subscribe"
    )
    await message.answer(
        text="Choose conversion",
        reply_markup=reply_markup,
    )


@dp.callback_query(FromRateCallback.filter())
async def from_currency_callback(callback: CallbackQuery, callback_data: FromRateCallback):
    reply_markup = await create_currencies_markup(
        currencies_repository=currencies_repository,
        from_currency_name=callback_data.name,
        page_size=PAGE_SIZE,
        command="track",
    )

    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Choose currency that you wanna get",
        reply_markup=reply_markup
    )


@dp.callback_query(ToRateCallback.filter())
async def to_currency_callback(callback: CallbackQuery, callback_data: ToRateCallback):
    from_currency_id = await currencies_repository.get_currency_id_by_name(callback_data.from_name)
    if not from_currency_id:
        await callback.bot.send_message(callback.message.chat.id, "smth went wrong")
    to_currency_id = await currencies_repository.get_currency_id_by_name(callback_data.name)
    if not to_currency_id:
        await callback.bot.send_message(callback.message.chat.id, "smth went wrong")
    await tracked_conversions_repository.add_currencies_pair(from_currency_id, to_currency_id)
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"{callback_data.from_name} -> {callback_data.name} is now tracked"
    )


@dp.callback_query(SubscribeCallback.filter())
async def subscribe_callback(callback: CallbackQuery, callback_data: SubscribeCallback):
    user_id = callback.from_user.id
    username = callback.from_user.username
    conversion_id = callback_data.conversion_id
    chat_id = callback.message.chat.id
    user = await users_repository.get_user_by_user_id(user_id)
    if not user:
        await users_repository.add_user(user_id, username, chat_id)
    await subscriptions_repository.add_subscription(user.id, conversion_id)
    conversion = await tracked_conversions_repository.get_conversion_by_id(conversion_id)
    await callback.bot.send_message(
        chat_id=chat_id,
        text=f"User {username} with id {user_id} is now subscribed for {conversion[1]} -> {conversion[2]}"
    )


@dp.callback_query(PaginationCallback.filter(F.command == "track"))
async def pagination_callback(callback: CallbackQuery, callback_data: PaginationCallback):
    reply_markup = await create_currencies_markup(
        currencies_repository=currencies_repository,
        from_currency_name=callback_data.from_currency,
        page_size=PAGE_SIZE,
        current_page=callback_data.page,
        command=callback_data.command
    )

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    await callback.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=reply_markup
    )


@dp.callback_query(PaginationCallback.filter(F.command == "subscribe"))
async def pagination_callback(callback: CallbackQuery, callback_data: PaginationCallback):
    reply_markup = await create_conversions_markup(
        currencies_repository=currencies_repository,
        page_size=PAGE_SIZE,
        current_page=callback_data.page,
        command=callback_data.command
    )

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    await callback.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=reply_markup
    )


async def init_conversions_list():
    conversions = await tracked_conversions_repository.get_all_conversions_with_names()
    for conversion in conversions:
        from_currency = conversion.from_currency_name
        to_currency = conversion.to_currency_name
        url = await craft_link(website_url, from_currency, to_currency)
        tracked_conversions.append({
            "id": conversion.id,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "url": url
        })


def create_async_thread():
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever).start()
    return loop


async def scan_conversion(url, conversion_id):
    rate, ascending = await parse_best_rate(url)

    date = datetime.now()

    rates_repository.add_rates({
        "conversion_id": conversion_id,
        "rate": rate,
        "ascending": ascending,
        "date": date
    })

    curr_time = datetime.now()
    week_before = curr_time - timedelta(weeks=1)

    max_weekly_rate = rates_repository.get_max_rate_by_conv_id_for_period(
        conversion_id, week_before, curr_time
    )
    if rate > max_weekly_rate:
        await notify_subscribed_users(conversion_id) # ну сделать крч надо


async def notify_subscribed_users(bot: Bot, conversion_id, period_start, period_end):
    subscriptions = await subscriptions_repository.get_subscription_info_by_conversion_id(conversion_id)
    subscriptions = subscriptions.all()
    
    for subscription in subscriptions:
        await bot.send_message(
            subscription.chat_id,
            f"{subscription.from_currency_name} -> {subscription.to_currency_name} is now highest for the period {period_start} -> {period_end}"
        )
    
    

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    currencies_page = await currencies_repository.get_currencies_page(0, 10)

    if not currencies_page.scalars().all():
        names_list = parse_currencies_from_html(website_url)

        if not names_list:
            print("Smth went wrong")
            return

        await currencies_repository.add_currencies(names_list)
    
    await init_conversions_list()

    await notify_subscribed_users(bot, 1)

    # loop = create_async_thread()
    

    # for num, conversion in enumerate(tracked_conversions):
    #     asyncio.run_coroutine_threadsafe(scan_conversion(conversion["url"], num), loop)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
