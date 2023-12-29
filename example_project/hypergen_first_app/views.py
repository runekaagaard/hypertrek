from hypergen.imports import *

from contextlib import contextmanager

from hypertrek import trek
from hypergen_first_app.treks import poc_trek

@contextmanager
def base_template():
    """
    This base template is meant to be shared between your views.
    """
    doctype()
    with html():
        with head():
            title("Hypertrek Hypergen Example")
            link("https://unpkg.com/simpledotcss@2.0.7/simple.min.css")
        with body():
            h1("Hypertrek Hypergen Example")

            with div(id_="content"):
                yield

base_template.target_id = "content"

def trek_template(concerns, state):
    inpt = concerns["rendering"]["hypergen"]()
    button("Commit", id_="commit", onclick=callback(commit_mission, state, inpt))
    hprint(state=state)
    with p():
        if not state["hypertrek"]["left_edge"]:
            button("<-", id_="previous", onclick=callback(bck, state))
        span(" ")
        if not state["hypertrek"]["right_edge"]:
            button("->", id_="next", onclick=callback(fwd, state, inpt))

@liveview(perm=NO_PERM_REQUIRED, base_template=base_template)
def show_trek(request):
    poc = poc_trek()
    state = trek.new_state()
    cmd, state, concerns = trek.get(poc, state)
    assert cmd == trek.RETRY
    trek_template(concerns, state)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def commit_mission(request, state, inpt):
    poc = poc_trek()
    cmd, state, concerns = trek.post(poc, state, inpt)
    if cmd == trek.CONTINUE:
        state = trek.forward(poc, state)
        cmd, state, concerns = trek.get(poc, state)

    trek_template(concerns, state)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def bck(request, state):
    poc = poc_trek()
    state = trek.backward(poc, state)
    cmd, state, concerns = trek.get(poc, state)

    trek_template(concerns, state)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def fwd(request, state, inpt):
    poc = poc_trek()
    cmd, state, concerns = trek.post(poc, state, inpt)
    if cmd == trek.CONTINUE:
        state = trek.forward(poc, state)
        cmd, state, concerns = trek.get(poc, state)

    trek_template(concerns, state)
