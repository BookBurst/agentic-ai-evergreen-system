import os
from pathlib import Path
from openai import OpenAI

def load_env(path=".env"):
    # Copy each KEY=value line of .env into the environment
    for line in Path(path).read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

load_env()
client = OpenAI(api_key=os.environ["API_KEY"],
                base_url=os.environ.get("BASE_URL") or None)
reply = client.chat.completions.create(
    model=os.environ["MODEL_NAME"],
    messages=[{"role": "user",
               "content": "Reply with exactly: setup OK"}],
)
print(reply.choices[0].message.content)
