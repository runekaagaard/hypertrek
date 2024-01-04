d = dict
from hypergen.imports import *

from contextlib import contextmanager

from hypertrek import hypertrek
from hypergen_first_app.treks import example_trek

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

def trek_template(trek, state, mission, as_args, as_kwargs):
    min_, max_, current = hypertrek.progress(trek, state)
    progress(value=current / ((max_+min_) / 2), style=d(width="100%"))
    p("On page ", current, " out of minimum ", min_, " and maximum ", max_, ".")

    inpt = mission.as_hypergen(*as_args, **as_kwargs)
    if not state["hypertrek"]["at_end"]:
        with p():
            button("Send", id_="commit", onclick=callback(post, state, inpt))
    hprint(state=state)
    with p():
        if not state["hypertrek"]["at_beginning"]:
            button("<-", id_="previous", onclick=callback(bck, state))
        span(" ")
        if not state["hypertrek"]["at_end"]:
            button("->", id_="next", onclick=callback(fwd, state, inpt))

@liveview(perm=NO_PERM_REQUIRED, base_template=base_template)
def get(request):
    trek = example_trek()
    state = hypertrek.new_state()
    cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state)
    assert cmd == hypertrek.RETRY
    trek_template(trek, state, mission, as_args, as_kwargs)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def post(request, state, inpt):
    trek = example_trek()
    cmd, state, mission, (as_args, as_kwargs) = hypertrek.post(trek, state, inpt)
    if cmd == hypertrek.CONTINUE:
        state = hypertrek.forward(trek, state)
        cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state)

    trek_template(trek, state, mission, as_args, as_kwargs)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def bck(request, state):
    trek = example_trek()
    state = hypertrek.backward(trek, state)
    cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state)

    trek_template(trek, state, mission, as_args, as_kwargs)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def fwd(request, state, inpt):
    trek = example_trek()
    cmd, state, mission, (as_args, as_kwargs) = hypertrek.post(trek, state, inpt)
    if cmd == hypertrek.CONTINUE:
        state = hypertrek.forward(trek, state)
        cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state)

    trek_template(trek, state, mission, as_args, as_kwargs)
