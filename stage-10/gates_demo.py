from gates import handle
from tracing import client, MODEL

SYSTEM = ('You handle refund requests for an online shop. '
          'Reply with JSON only: {"action": "refund" or '
          '"reply", "amount": a number of dollars}.')

def propose(message):
    reply = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": message}])
    return reply.choices[0].message.content

def show(text):
    verdict, detail = handle(text)
    print(f"{verdict:<7}{text}")
    if verdict != "run":
        print("       ", detail)

if __name__ == "__main__":
    show(propose("Order 5521 arrived broken. Please refund "
                 "the 35 dollars."))
    show(propose("I was charged 480 dollars twice. Fix it."))
    # Three broken proposals in a row trip the stop
    for text in ["I will refund it", "{}",
                 '{"action": "wire", "amount": 5}']:
        show(text)
    show("one more")
