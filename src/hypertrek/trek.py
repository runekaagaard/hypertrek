CONTINUE, RETRY, TERMINATED = "CONTINUE", "RETRY", "TERMINATED"
FORWARD, BACKWARD = "FORWARD", "BACKWARD"

def init(trek):
    return trek(), {"mission_index": 0}

def execute(trek, state, inpt=None):
    if inpt is None:
        inpt = {}
    return trek[state["mission_index"]](state=state, inpt=inpt)

def forward(trek, state=None, inpt=None):
    if state["mission_index"] + 1 > len(trek) - 1:
        return True, state
    else:
        state["mission_index"] += 1
        return False, state

def backward(trek, state):
    state["mission_index"] = max(state["mission_index"] - 1, 0)

    return False, state
