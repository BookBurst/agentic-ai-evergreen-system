import json
from check import client, MODEL

RUBRIC = [
    "Names the largest spending category",
    "Uses only numbers that appear in the data",
    "Stays neutral: no advice, no judgment of the spender",
    "Has two sentences or fewer",
]

def judge(summary, data):
    # A second model call that grades the summary
    system = ("You grade a summary against a rubric. For each "
              "criterion answer pass or fail and quote the "
              "words that prove it. Grade only what is "
              "written. Reply as JSON: "
              '{"grades": [{"criterion": "...", '
              '"result": "pass or fail", "evidence": "..."}]}')
    user = json.dumps({"data": data, "summary": summary,
                       "rubric": RUBRIC})
    reply = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}])
    answer = json.loads(reply.choices[0].message.content)
    return answer["grades"]

if __name__ == "__main__":
    data = {"total": 1263.44, "currency": "USD",
            "by_category": {"Travel": 548.35, "Office": 280.30,
                            "Software": 273.14,
                            "Meals": 161.65}}
    summaries = [
        "October spending came to $1,263.44. Travel was the "
        "largest category at $548.35.",
        "October spending reached $1,300, mostly on travel. "
        "You should cut back on flights next month."]
    for text in summaries:
        print(text)
        for g in judge(text, data):
            print(f"  {g['result']:4}  {g['criterion']}")
