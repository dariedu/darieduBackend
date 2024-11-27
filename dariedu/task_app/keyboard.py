import json


def keyboard_task(data):
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "Подтвердить участие", "callback_data": f"accept_task:{json.dumps(data)}"},
                {"text": "Отказаться", "callback_data": f'refuse_task:{json.dumps(data)}'}
            ]
        ]
    }
    return inline_keyboard


def keyboard_delivery(data):
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "Подтвердить участие", "callback_data": "accept_delivery"},
                {"text": "Отказаться", "callback_data": f'refuse_delivery:{json.dumps(data)}'}
            ]
        ]
    }
    return inline_keyboard
