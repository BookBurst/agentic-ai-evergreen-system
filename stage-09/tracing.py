import json, os, time
from pathlib import Path
from openai import OpenAI

def load_env(path=".env"):
    # Copy each KEY=value line of .env into the environment
    for line in Path(path).read_text("utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

load_env()
client = OpenAI(api_key=os.environ["API_KEY"],
                base_url=os.environ.get("BASE_URL") or None)
MODEL = os.environ["MODEL_NAME"]
TRACE = Path("trace.jsonl")

def record(agent, kind, **fields):
    # One line in the trace file for each thing that happens
    entry = {"time": time.strftime("%H:%M:%S"),
             "agent": agent, "kind": kind, **fields}
    with TRACE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def call(agent, messages, **options):
    # One model call that writes down its cost and its time
    start = time.time()
    reply = client.chat.completions.create(
        model=MODEL, messages=messages,
        **options)
    usage = reply.usage
    record(agent, "model", tokens_in=usage.prompt_tokens,
           tokens_out=usage.completion_tokens,
           seconds=round(time.time() - start, 1))
    return reply.choices[0].message
