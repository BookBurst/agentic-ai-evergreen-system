import re
from pathlib import Path

PATTERNS = [
    r"sk-[A-Za-z0-9_-]{20,}",
    r"(?i)(api_?key|token|secret)\s*=\s*[\"'][^\"']{12,}[\"']",
]
SKIP = {".git", ".venv", "__pycache__", "node_modules"}

def scan(folder="."):
    problems = []
    for path in Path(folder).rglob("*"):
        if SKIP & set(path.parts) or not path.is_file():
            continue
        if path.name == ".env" or path.stat().st_size > 10**6:
            continue
        text = path.read_text("utf-8", errors="ignore")
        if any(re.search(p, text) for p in PATTERNS):
            problems.append(f"{path}: looks like a key")
    ignore = Path(folder) / ".gitignore"
    lines = []
    if ignore.exists():
        lines = ignore.read_text("utf-8").split()
    listed = ".env" in lines
    if not listed:
        problems.append(".gitignore does not list .env")
    return problems

if __name__ == "__main__":
    found = scan()
    print("\n".join(found) if found else "Nothing found")
