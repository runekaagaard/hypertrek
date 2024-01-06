d = dict

from functools import wraps

CONTINUE, RETRY, UNDECIDABLE = "CONTINUE", "RETRY", "UNDECIDABLE"

### Trek ###

TREKS = {}

def trek(*, title):
    hypertrek = d(title=title)
    def _(f):
        f.hypertrek = hypertrek
        TREKS[f] = d(title=title)

        @wraps(f)
        def __(*args, **kwargs):
            return f(*args, **kwargs)

        __.hypertrek = hypertrek
        return __

    return _

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
    hypertrek = state["hypertrek"]
    while True:
        hypertrek["i"] = min(hypertrek["i"] + 1, len(trek) - 1)
        if hypertrek["i"] == len(trek) - 1 or trek[hypertrek["i"]].is_visible(state):
            return mark_begin_end(trek, state)

def backward(trek, state):
    hypertrek = state["hypertrek"]

    while True:
        hypertrek["i"] = max(hypertrek["i"] - 1, 0)
        if hypertrek["i"] == 0 or trek[hypertrek["i"]].is_visible(state):
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

def input_from_request(trek, state, request):
    assert request.method == "POST"
    hypertrek = state["hypertrek"]
    return trek[hypertrek["i"]].input_from_request(request)

def mark_begin_end(trek, state):
    state["hypertrek"]["at_beginning"] = state["hypertrek"]["i"] == 0
    state["hypertrek"]["at_end"] = state["hypertrek"]["i"] == len(trek) - 1

    return state

### Mission ###

class mission():
    def __init__(self, when=None):
        self.when = when

    def progress(self, state):
        is_visible = self.is_visible(state)
        if is_visible == UNDECIDABLE:
            return (0, 1, 0)
        elif is_visible is True:
            return (1, 1, 1)
        elif is_visible is False:
            return (0, 0, 0)
        else:
            raise Exception(f"Invalid return value: {repr(is_visible)} from is_visible")

    def is_visible(self, state):
        if self.when is None:
            return True
        else:
            return self.when(state)
