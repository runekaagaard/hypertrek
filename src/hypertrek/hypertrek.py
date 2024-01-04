d = dict

from functools import wraps
from toolz import curry

CONTINUE, RETRY = "CONTINUE", "RETRY"

### Trek ###

TREKS = {}

def trek(*, title):
    hypertrek = d(title=title)
    def _(f):
        f.hypertrek = hypertrek
        TREKS[f] = d(title=title)

        @curry
        @wraps(f)
        def __(*args, **kwargs):
            return f(*args, **kwargs)

        __.hypertrek = hypertrek
        return __

    return _

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

    return trek[hypertrek["i"]].execute(state=state, first=first, method="get")

def post(trek, state, inpt):
    hypertrek = state["hypertrek"]
    first = hypertrek["i"] not in hypertrek["visited"]
    hypertrek["visited"].add(hypertrek["i"])

    return trek[hypertrek["i"]].execute(state=state, inpt=inpt, first=first, method="post")

def forward(trek, state):
    state["hypertrek"]["i"] = min(state["hypertrek"]["i"] + 1, len(trek) - 1)

    return mark_begin_end(trek, state)

def backward(trek, state):
    state["hypertrek"]["i"] = max(state["hypertrek"]["i"] - 1, 0)

    return mark_begin_end(trek, state)

def progress(trek, state):
    min_, max_, current = 0, 0, 0
    for i, mission in enumerate(trek):
        min2, max2, current2 = mission.progress(state)
        min_ += min2
        max_ += max2
        if i <= state["hypertrek"]["i"]:
            current += current2

    return min_, max_, current

### Mission ###

class mission():
    def __init__(self, when=None):
        self.when = when

    def progress(self, state):
        if self.is_visible(state):
            return (1, 1, 1)
        else:
            return (0, 0, 0)

    def is_visible(self, state):
        return self.when is None or self.when(state)
