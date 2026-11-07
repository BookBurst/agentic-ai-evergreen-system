import json
from approvals import request, approve, PENDING, OUTBOX
from auditlog import LOG, verify

LOG.unlink(missing_ok=True)
args = {"to": "sales@pinecrest.example", "subject": "Quote",
        "body": "Could you send a quote for 10 cartons?"}
for tool in ["read_note", "send_email", "delete_all"]:
    answer = request("writer", "run1", tool, args)
    print(f"{tool:<11}->", answer)

path = next(PENDING.glob("*.json"))
item = json.loads(path.read_text("utf-8"))
item["args"]["to"] = "someone@else.example"  # in transit
path.write_text(json.dumps(item), "utf-8")
print("tampered   ->", approve(path.stem))

item["args"]["to"] = "sales@pinecrest.example"
path.write_text(json.dumps(item), "utf-8")
print("approved   ->", approve(path.stem))
print(OUTBOX.read_text("utf-8").strip())
print(verify())
