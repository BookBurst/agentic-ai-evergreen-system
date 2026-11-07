import json
import os
import urllib.error
import urllib.request
from pathlib import Path

# Read API_KEY, MODEL_NAME and BASE_URL from .env
for line in Path(".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

base = os.environ.get("BASE_URL") or "https://api.openai.com/v1"
url = base.rstrip("/") + "/chat/completions"
body = {"model": os.environ["MODEL_NAME"],
        "messages": [{"role": "user",
                      "content": "Reply with exactly: hello"}]}

request = urllib.request.Request(
    url, method="POST",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json",
             "Authorization":
                 "Bearer " + os.environ["API_KEY"]})

try:
    with urllib.request.urlopen(request, timeout=60) as resp:
        print("Status:", resp.status)
        data = json.loads(resp.read())
        print(data["choices"][0]["message"]["content"])
except urllib.error.HTTPError as err:
    print("Status:", err.code)
    print(err.read().decode("utf-8")[:300])
