import json, os, urllib.request

for line in open(".env"):
    if "=" in line and not line.startswith("#"):
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

TOKEN = os.environ["BOT_TOKEN"]
OWNERS = {int(os.environ["OWNER_ID"])}  # allowed user IDs
URL = os.environ.get("TELEGRAM_API", "https://api.telegram.org")

def tg(method, **params):
    # One outgoing call to the Telegram Bot API
    request = urllib.request.Request(
        f"{URL}/bot{TOKEN}/{method}",
        data=json.dumps(params).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=40) as answer:
        return json.load(answer)["result"]

def ask_approval(chat_id, text):
    buttons = [[{"text": "Approve", "callback_data": "approve"},
                {"text": "Reject", "callback_data": "reject"}]]
    tg("sendMessage", chat_id=chat_id, text=text,
       reply_markup={"inline_keyboard": buttons})

def handle(update):
    query = update.get("callback_query")
    source = query or update.get("message")
    if not source or source["from"]["id"] not in OWNERS:
        return  # strangers get no answer at all
    if query:
        tg("answerCallbackQuery", callback_query_id=query["id"])
        print("decision:", query["data"])
    elif source.get("text") == "/ask":
        ask_approval(source["chat"]["id"],
                     "Send the weekly report to the client?")

if __name__ == "__main__":
    offset = 0
    while True:
        updates = tg("getUpdates", offset=offset, timeout=30)
        for update in updates:
            offset = update["update_id"] + 1
            handle(update)
