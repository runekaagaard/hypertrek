d = dict

from hypergen.imports import loads, dumps

import os, fcntl
from functools import wraps
from uuid import uuid4

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

## State modifying operators ##

def new_state(store=None):
    state = {"hypertrek": {"i": 0, "visited": set(), "at_beginning": True, "at_end": False}}
    if store:
        store.put(state)
    return state

def get(trek, state, store=None):
    hypertrek = state["hypertrek"]
    first = hypertrek["i"] not in hypertrek["visited"]
    hypertrek["visited"].add(hypertrek["i"])
    result = trek[hypertrek["i"]].execute(state=state, first=first, method="get")
    if store:
        store.put(state)

    return result

def post(trek, state, inpt, store=None):
    hypertrek = state["hypertrek"]
    first = hypertrek["i"] not in hypertrek["visited"]
    hypertrek["visited"].add(hypertrek["i"])
    result = trek[hypertrek["i"]].execute(state=state, inpt=inpt, first=first, method="post")
    if store:
        store.put(state)

    return result

def forward(trek, state, store=None):
    hypertrek = state["hypertrek"]
    while True:
        hypertrek["i"] = min(hypertrek["i"] + 1, len(trek) - 1)
        if hypertrek["i"] == len(trek) - 1 or trek[hypertrek["i"]].is_visible(state):
            state = mark_begin_end(trek, state)
            if store:
                store.put(state)

            return state

def backward(trek, state, store=None):
    hypertrek = state["hypertrek"]
    while True:
        hypertrek["i"] = max(hypertrek["i"] - 1, 0)
        if hypertrek["i"] == 0 or trek[hypertrek["i"]].is_visible(state):
            state = mark_begin_end(trek, state)
            if store:
                store.put(state)

            return state

def rewind(trek, state, store=None):
    hypertrek = state["hypertrek"]
    hypertrek["i"] = 0
    state = mark_begin_end(trek, state)
    if store:
        store.put(state)

    return state

## Stores ##

class JsonStore:
    def __init__(self, uuid=None, path="/tmp/hypertrek/{uuid}.json"):
        self.uuid = str(uuid4()) if uuid is None else uuid
        self.path = path

    def get_path(self):
        return self.path.format(uuid=self.uuid)

    def ensure_path(self):
        directory = os.path.dirname(self.get_path())
        if not os.path.exists(directory):
            os.makedirs(directory)

    def get(self):
        self.ensure_path()

        with open(self.get_path(), "r") as f:
            return loads(f.read())

    def put(self, state):
        self.ensure_path()

        with open(self.get_path(), "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(dumps(state))
            fcntl.flock(f, fcntl.LOCK_UN)

class ModelStore:
    def __init__(self, uuid=None):
        self.uuid = str(uuid4()) if uuid is None else uuid

    def get(self):
        from hypertrek.models import TrekState
        return loads(TrekState.objects.get(uuid=self.uuid).value)

    def put(self, state):
        from hypertrek.models import TrekState
        trek_state, _ = TrekState.objects.get_or_create(uuid=self.uuid)
        trek_state.value = dumps(state)
        trek_state.save()

## Helpers ##

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
