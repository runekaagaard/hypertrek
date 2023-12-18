CONTINUE, RETRY = "CONTINUE", "RETRY"

def forward(trek, state=None, inpt=None):
    if state is None:
        state = {"mission_index": 0}
    else:
        state["mission_index"] += 1

    state = trek()[state["mission_index"]](state=state, inpt=inpt)

    return state

def backward(trek):
    pass
