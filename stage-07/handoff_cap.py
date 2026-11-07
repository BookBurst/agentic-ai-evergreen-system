MAX_PASSES = 4   # times one task may change hands

def hand_off(task_id, receiver, passes):
    # passes counts how often each task changed hands
    passes[task_id] = passes.get(task_id, 0) + 1
    if passes[task_id] > MAX_PASSES:
        return "you"              # a person settles it
    return receiver

if __name__ == "__main__":
    # Two agents that each think the other should decide
    task_id = "T-118: pick the newsletter subject line"
    passes, holder = {}, "writer"
    while holder != "you":
        other = "editor" if holder == "writer" else "writer"
        holder = hand_off(task_id, other, passes)
        print(f"pass {passes[task_id]}: now with {holder}")
