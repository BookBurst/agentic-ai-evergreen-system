from pathlib import Path

ALLOWED = Path("workspace").resolve()

def safe_path(name):
    # Turn a requested name into a full path, or refuse it
    path = (ALLOWED / name).resolve()
    if not path.is_relative_to(ALLOWED):
        raise PermissionError(f"{name!r} is outside the folder")
    return path

def read_note(name):
    return safe_path(name).read_text("utf-8")

if __name__ == "__main__":
    ALLOWED.mkdir(exist_ok=True)
    (ALLOWED / "notes.txt").write_text("buy milk", "utf-8")
    for name in ["notes.txt", "../.env",
                 "../workspace-old/a.txt"]:
        try:
            print(f"{name:<22}", read_note(name))
        except PermissionError:
            print(f"{name:<22}", "refused")
