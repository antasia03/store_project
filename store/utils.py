import requests

TELEGRAM_BOT_TOKEN = '7522189041:AAFGo51Ao3X869i_Y25PvExBt2Ym5gQqs-E'

# TELEGRAM_CHAT_ID = '828477672'

def send_telegram_notification(telegram_user_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': str(telegram_user_id),
        'text': message,
    }
    response = requests.post(url, data=payload)
    return response
