import base64, json, os
from pathlib import Path
from openai import OpenAI

def load_env(path=".env"):
    for line in Path(path).read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

load_env()
client = OpenAI(api_key=os.environ["API_KEY"],
                base_url=os.environ.get("BASE_URL") or None)
MODEL = os.environ["MODEL_NAME"]

ASK = """Read this receipt. Reply with JSON only, in this shape:
{"store": "...", "items": [{"name": "...", "price": 0.0}],
 "subtotal": 0.0, "tax": 0.0, "total": 0.0}
Copy every number exactly as printed."""

def ask(image_path=None):
    content = [{"type": "text", "text": ASK}]
    if image_path:
        data = base64.b64encode(Path(image_path).read_bytes())
        content.append({"type": "image_url", "image_url": {
            "url": "data:image/png;base64," + data.decode()}})
    return client.chat.completions.create(
        model=MODEL, max_completion_tokens=800,
        messages=[{"role": "user", "content": content}])

def check(data):
    # Problems found by plain arithmetic, not by the model
    problems = []
    items = round(sum(i["price"] for i in data["items"]), 2)
    if items != data["subtotal"]:
        problems.append(f"items add up to {items}, "
                        f"subtotal says {data['subtotal']}")
    expected = round(data["subtotal"] + data["tax"], 2)
    if expected != data["total"]:
        problems.append(f"subtotal + tax is {expected}, "
                        f"total says {data['total']}")
    return problems

if __name__ == "__main__":
    plain = ask().usage.prompt_tokens
    reply = ask("receipt.png")
    print("tokens in, text only:", plain)
    print("tokens in, with image:", reply.usage.prompt_tokens)
    text = reply.choices[0].message.content
    data = json.loads(text.strip().strip("`")
                      .removeprefix("json"))
    print(json.dumps(data))
    print("problems:", check(data) or "none")
