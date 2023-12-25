d = dict

class _null:
    def __str__(self):
        return "null"

    def __repr__(self):
        return "null"

null = _null()

def my_mission_render_debug(data, errors, is_valid, error_message):
    def _():
        return f"data = {data}, errors = {errors}, is_valid = {is_valid}, error_message = {error_message}"

    return _

def my_mission(fields):
    def _(state, inpt=None):
        if inpt is None:
            inpt = {}
        data = {x: inpt.get(x, state.get(x, null)) for x in fields}
        errors = {x for x in data.keys() if data.get(x) != x}
        is_valid = not errors

        error_message = None
        if not is_valid and inpt:
            error_message = "booh: " + ", ".join(errors)

        if is_valid and inpt:
            state |= inpt

        debug = my_mission_render_debug(data, errors, is_valid, error_message)
        return ("cont" if is_valid else "retry"), state, d(rendering=d(debug=debug))

    return _

def my_trek():
    return [
        my_mission("abc"),
        my_mission("def"),
        my_mission("gh"),
    ]

def init_state():
    return {"i": 0}

def execute(trek, state, mission_input=None, debug=False):
    mission = trek[state["i"]]
    cmd, state, concerns = mission(state, inpt=mission_input)

    if debug:
        print("execute:", cmd, state)
        print("rendering:", concerns["rendering"]["debug"]())

    return cmd, state, concerns

def fwd(trek, state):
    if state["i"] + 1 > len(trek) - 1:
        print("fwd:", True, state)
        return True, state
    else:
        state["i"] += 1
        print("fwd:", False, state)
        return False, state

    return state

def bck(trek, state):
    state["i"] = max(0, state["i"] - 1)
    print("bck:", state)

    return False, state

trek = my_trek()
is_done, state = False, init_state()

while is_done is False:
    cmd, state, concerns = execute(trek, state)
    print("rendering:", concerns["rendering"]["debug"]())
    while True:
        inpt = input("? ").strip()
        if inpt == "bck":
            direction = bck
            break
        else:
            if inpt == "fwd":
                inpt = None
            else:
                inpt = {x: x for x in inpt}
            cmd, state, concerns = execute(trek, state, inpt)
            if cmd == "cont":
                direction = fwd
                break
            else:
                print("rendering:", concerns["rendering"]["debug"]())

    is_done, state = direction(trek, state)

def manual_execution():
    global trek, state
    cmd, state, concerns = execute(trek, state, debug=True)  # retry
    cmd, state, concerns = execute(trek, state, d(a="a", b="b", c="x"), debug=True)  # retry
    cmd, state, concerns = execute(trek, state, d(a="a", b="b", c="c"), debug=True)  # continue
    is_done, state = fwd(trek, state)
    cmd, state, concerns = execute(trek, state, debug=True)  # retry
    state = bck(trek, state)
    cmd, state, concerns = execute(trek, state, debug=True)  # continue
    is_done, state = fwd(trek, state)
    cmd, state, concerns = execute(trek, state, debug=True)  # retry
    cmd, state, concerns = execute(trek, state, d(d="d", e="e", f="f"), debug=True)  # continue
    is_done, state = fwd(trek, state)
    cmd, state, concerns = execute(trek, state, d(g="g", h="h"), debug=True)  # continue
    is_done, state = fwd(trek, state)
    print("result:", state)

# manual_execution()
