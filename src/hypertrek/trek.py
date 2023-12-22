CONTINUE, RETRY, TERMINATED = "CONTINUE", "RETRY", "TERMINATED"
FORWARD, BACKWARD = "FORWARD", "BACKWARD"

def forward(trek, state=None, inpt=None):
    missions = trek()

    if state is None:
        state = {"mission_index": 0}
    if "mission_index" not in state:
        state["mission_index"] = 0

    command, state, side_effects = missions[state["mission_index"]](state=state, inpt=inpt)

    if command == CONTINUE:
        state["mission_index"] += 1

    if state["mission_index"] > len(missions) - 1:
        command = TERMINATED

    return command, state, side_effects

def backward(trek):
    pass
