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
MODEL = os.environ["MODEL_NAME"]
from pathlib import Path

WORKDIR = Path("workspace").resolve()  # tools stay in here

# 1. The function: plain Python that does one job
def list_files(folder="."):
    path = (WORKDIR / folder).resolve()
    if not path.is_relative_to(WORKDIR):   # blocks ../ tricks
        return {"error": "That folder is outside workspace."}
    return sorted(p.name for p in path.iterdir())

# 2. The schema: how the model learns the tool exists
LIST_FILES = {"type": "function", "function": {
    "name": "list_files",
    "description": "List the file names inside a folder.",
    "parameters": {
        "type": "object",
        "properties": {"folder": {
            "type": "string",
            "description": "Folder inside the workspace"}},
        "required": ["folder"]}}}

# 3. The registry: tool name -> real function
TOOLS = {"list_files": list_files}
SCHEMAS = [LIST_FILES]
import json

def run_tool(call):
    name = call.function.name
    args = call.function.arguments or "{}"
    try:
        result = TOOLS[name](**json.loads(args))
    except Exception as err:  # unknown tool, bad arguments
        result = {"error": f"{type(err).__name__}: {err}"}
    return json.dumps(result, default=str)
import json

MAX_STEPS = 6  # hard cap: the loop never runs forever

def run_agent(goal):
    messages = [{"role": "user", "content": goal}]
    for step in range(MAX_STEPS):
        msg = client.chat.completions.create(   # 1 think
            model=MODEL, messages=messages, tools=SCHEMAS,
        ).choices[0].message
        messages.append(msg)      # keep the model's own turn
        if not msg.tool_calls:
            return msg.content    # 4 decide: final answer
        for call in msg.tool_calls:             # 2 act
            args = json.loads(call.function.arguments)
            result = TOOLS[call.function.name](**args)
            messages.append({                   # 3 check
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result, default=str)})
    return "Stopped: step limit reached."
print(run_agent("List the files in the reports folder, then try the folder ../.."))
