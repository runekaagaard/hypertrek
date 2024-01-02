d = dict

from functools import wraps
from toolz import curry

CONTINUE, RETRY = "CONTINUE", "RETRY"

### Trek ###

def mark_begin_end(trek, state):
    state["hypertrek"]["at_beginning"] = state["hypertrek"]["i"] == 0
    state["hypertrek"]["at_end"] = state["hypertrek"]["i"] == len(trek) - 1

    return state

def new_state():
    return {"hypertrek": {"i": 0, "visited": set(), "at_beginning": True, "at_end": False}}

def get(trek, state):
    hypertrek = state["hypertrek"]
    first = hypertrek["i"] not in hypertrek["visited"]
    hypertrek["visited"].add(hypertrek["i"])

    return trek[hypertrek["i"]](state=state, first=first, method="get")

def post(trek, state, inpt):
    hypertrek = state["hypertrek"]
    first = hypertrek["i"] not in hypertrek["visited"]
    hypertrek["visited"].add(hypertrek["i"])

    return trek[hypertrek["i"]](state=state, inpt=inpt, first=first, method="post")

def forward(trek, state):
    state["hypertrek"]["i"] = min(state["hypertrek"]["i"] + 1, len(trek) - 1)

    return mark_begin_end(trek, state)

def backward(trek, state):
    state["hypertrek"]["i"] = max(state["hypertrek"]["i"] - 1, 0)

    return mark_begin_end(trek, state)

def progress(trek, state):
    min_, max_, current = 0, 0, 0
    for i, mission in enumerate(trek):
        min2, max2, current2 = mission._partial.func.hypertrek["progress"](state)
        min_ += min2
        max_ += max2
        if i <= state["hypertrek"]["i"]:
            current += current2

    return min_, max_, current

### Mission ###

def mission(*, concerns, configurator, progress):
    hypertrek = d(concerns=concerns, configurator=configurator, progress=progress)
    def _(f):
        f.hypertrek = hypertrek

        @curry
        @wraps(f)
        def __(*args, **kwargs):
            return f(*args, **kwargs)

        __.hypertrek = hypertrek
        return __

    return _
