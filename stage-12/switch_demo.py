from switch import STATE, Paused, check_switch, command

STATE.unlink(missing_ok=True)
STEPS = ["fetch", "summarize", "save", "send"]
DONE = {"researcher": [], "writer": []}

def run_job(agent):
    for step in STEPS:
        if step in DONE[agent]:
            continue                  # done before the pause
        try:
            check_switch()            # before every step
        except Paused as error:
            print(f"{agent} stopped: {error}")
            return
        print(f"{agent} runs {step}")
        DONE[agent].append(step)
        if agent == "researcher" and step == "summarize":
            print("you:", command("/pause"))   # from your phone
    print(f"{agent} finished")

run_job("researcher")
run_job("writer")
print("you:", command("/resume"))
run_job("researcher")
run_job("writer")
