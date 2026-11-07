import random
import sys
import time
import urllib.error
import urllib.request
from urllib.request import urlopen

# Worth trying again: the problem is theirs or passing
TEMPORARY = {408, 429, 500, 502, 503, 504}
TRIES = 5     # attempts in total
CAP = 30      # never wait longer than this many seconds

def pause_for(hint, wait):
    # Seconds to wait before the next try, or None to give up
    if hint and hint.isdigit():
        seconds = int(hint)          # the server named a time
        return seconds if seconds <= CAP else None
    return random.uniform(0, wait)   # random: no collisions

def out_of_credit(error):
    # Wording differs by provider: check yours
    text = error.read().decode("utf-8", "replace").lower()
    return "quota" in text or "credit" in text

def call_with_retries(request):
    wait = 1
    for attempt in range(1, TRIES + 1):
        try:
            with urlopen(request, timeout=20) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError) as error:
            code = getattr(error, "code", None)  # HTTP only
            if code and code not in TEMPORARY:
                raise    # 400, 401, 404: a retry cannot help
            if code == 429 and out_of_credit(error):
                raise    # waiting does not add credit
            hint = None
            if code:
                hint = error.headers.get("Retry-After")
            seconds = pause_for(hint, wait)
            if attempt == TRIES or seconds is None:
                raise    # leave the rest to the checkpoint
            print(f"try {attempt}: {code or 'no answer'}, "
                  f"waiting {seconds:.1f}s")
            time.sleep(seconds)
            wait = min(wait * 2, CAP)    # doubles, up to CAP

if __name__ == "__main__":
    request = urllib.request.Request(sys.argv[1])
    try:
        print(call_with_retries(request).decode()[:80])
    except urllib.error.HTTPError as error:
        print("gave up: HTTP", error.code)
    except (urllib.error.URLError, TimeoutError):
        print("gave up: no answer")
