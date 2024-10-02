from aiogram.filters.callback_data import CallbackData

class PaginationCallback(CallbackData, prefix='pagination'):
    action: str
    page: int
    command: str
    from_currency: str|None

class FromRateCallback(CallbackData, prefix='from'):
    name: str

class ToRateCallback(CallbackData, prefix='to'):
    name: str
    from_name: str

class SubscribeCallback(CallbackData, prefix='subs'):
    conversion_id: int
