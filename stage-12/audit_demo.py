from auditlog import LOG, write_event, verify

LOG.unlink(missing_ok=True)
write_event("researcher", "run1", "ask", "before", "notes")
write_event("researcher", "run1", "ask", "after", "summary")
write_event("writer", "run1", "ask", "after", "draft")
print("1.", verify())

lines = LOG.read_text("utf-8").splitlines()
changed = list(lines)
changed[1] = changed[1].replace("run1", "run9")  # edit
LOG.write_text("\n".join(changed) + "\n", "utf-8")
print("2.", verify())

del lines[1]                                     # remove
LOG.write_text("\n".join(lines) + "\n", "utf-8")
print("3.", verify())
