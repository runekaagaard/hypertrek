CONTINUE, RETRY, TERMINATE = "CONTINUE", "RETRY", "TERMINATE"

__all__ = ["new_state", "get", "post", "forward", "backward", "pageno", "CONTINUE", "RETRY", "TERMINATE"]

def edges(trek, state):
    state["hypertrek"]["left_edge"] = state["hypertrek"]["i"] == 0
    state["hypertrek"]["right_edge"] = state["hypertrek"]["i"] == len(trek) - 1

    return state

def new_state():
    return {"hypertrek": {"i": 0, "visited": set(), "left_edge": True, "right_edge": False}}

def get(trek, state):
    hypertrek = state["hypertrek"]
    first = hypertrek["i"] not in hypertrek["visited"]
    hypertrek["visited"].add(hypertrek["i"])

    return trek[hypertrek["i"]](state=state, first=first, method="get")

def post(trek, state, inpt):
    assert inpt
    hypertrek = state["hypertrek"]
    first = hypertrek["i"] not in hypertrek["visited"]
    hypertrek["visited"].add(hypertrek["i"])

    return trek[hypertrek["i"]](state=state, inpt=inpt, first=first, method="post")

def forward(trek, state):
    state["hypertrek"]["i"] = min(state["hypertrek"]["i"] + 1, len(trek) - 1)

    return edges(trek, state)

def backward(trek, state):
    state["hypertrek"]["i"] = max(state["hypertrek"]["i"] - 1, 0)

    return edges(trek, state)

def pageno(trek, state):
    result = [0, 0]
    for mission in trek:
        pno = mission._partial.func.hypertrek["pageno"](state)
        result[0] += pno[0]
        result[1] += pno[1]

    return result
