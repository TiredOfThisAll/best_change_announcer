from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from callbacks import PaginationCallback, FromRateCallback, ToRateCallback, SubscribeCallback
from data.repository.currencies import CurrenciesRep
from data.repository.tracked_conversions import TrackedConversionsRep


def create_pagination_keyboard(
        page: list,
        row_callback_data: list,
        current_page: int,
        total_pages: int,
        command: str,
        from_currency_name: str|None = None
    ):
    builder = InlineKeyboardBuilder()

    # Add rows
    for num, row in enumerate(page):
        builder.row(InlineKeyboardButton(
            text=row[1],
            callback_data=row_callback_data[num]
        ))

    # Add pagination controls
    pagination_row = []
    if current_page > 0:
        pagination_row.append(InlineKeyboardButton(
            text='«',
            callback_data=PaginationCallback(
                action="prev",
                page=str(current_page-1),
                command=command,
                from_currency=from_currency_name
            ).pack())
        )
    else:
        pagination_row.append(InlineKeyboardButton(text='«', callback_data='noop'))

    pagination_row.append(
        InlineKeyboardButton(text=f'{current_page}/{total_pages}', callback_data='noop')
    )

    if current_page < total_pages:
        pagination_row.append(InlineKeyboardButton(
            text='»',
            callback_data=PaginationCallback(
                action="next",
                page=str(current_page+1),
                command=command,
                from_currency=from_currency_name
            ).pack())
        )
    else:
        pagination_row.append(InlineKeyboardButton(text='»', callback_data='noop'))
    
    builder.row(*pagination_row)

    return builder.as_markup()


async def create_currencies_markup(
        currencies_repository: CurrenciesRep,
        from_currency_name: str|None = None,
        page_size: int = 10,
        current_page: int = 0,
        command: str = "noop"
    ):
    page = await currencies_repository.get_currencies_page(current_page * page_size, page_size * current_page + page_size - 1)
    page = page.all()
    max_page = await currencies_repository.get_currency_quantity() // page_size

    callback_data = []
    if from_currency_name:
        callback_data = [ToRateCallback(name=row[1], from_name=from_currency_name).pack() for row in page]
    else:
        callback_data = [FromRateCallback(name=row[1]).pack() for row in page]
    reply_markup=create_pagination_keyboard(page, callback_data, current_page, max_page, command, from_currency_name)
    return reply_markup


async def create_conversions_markup(
        conversions_repository: TrackedConversionsRep,
        page_size: int = 10,
        current_page: int = 0,
        command: str = "noop"
    ):
    page = await conversions_repository.get_page(0, 10)
    conversions_quantity = await conversions_repository.get_conversions_quantity()
    max_page = conversions_quantity // page_size
    
    callback_data = [SubscribeCallback(conversion_id=row.id).pack() for row in page]

    page = [[row.id, row.to_currency_name + " -> " + row.from_currency_name] for row in page]

    reply_markup = create_pagination_keyboard(page, callback_data, current_page, max_page, command)
    return reply_markup
