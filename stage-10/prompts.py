from pathlib import Path

PROMPTS = Path("prompts")

def load(name, version=None):
    # name.current holds the live version number, such as 2
    if version is None:
        pointer = PROMPTS / f"{name}.current"
        version = pointer.read_text("utf-8").strip()
    path = PROMPTS / f"{name}_v{version}.txt"
    return version, path.read_text("utf-8")
