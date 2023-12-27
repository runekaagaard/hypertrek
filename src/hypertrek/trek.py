CONTINUE, RETRY, TERMINATED = "CONTINUE", "RETRY", "TERMINATED"
FORWARD, BACKWARD = "FORWARD", "BACKWARD"

def init(trek):
    return trek(), {"hypertrek": {"i": 0, "executed": set()}}

def execute(trek, state, inpt=None):
    if inpt is None:
        inpt = {}

    hypertrek = state["hypertrek"]
    first = hypertrek["i"] not in hypertrek["executed"]
    hypertrek["executed"].add(hypertrek["i"])

    return trek[hypertrek["i"]](state=state, inpt=inpt, first=first)

def forward(trek, state=None):
    if state["hypertrek"]["i"] + 1 > len(trek) - 1:
        return True, state
    else:
        state["hypertrek"]["i"] += 1
        return False, state

def backward(trek, state):
    state["hypertrek"]["i"] = max(state["hypertrek"]["i"] - 1, 0)

    return False, state

def pageno(trek, state):
    result = [0, 0]
    for mission in trek:
        pno = mission._partial.func.hypertrek["pageno"](state)
        result[0] += pno[0]
        result[1] += pno[1]

    return result
