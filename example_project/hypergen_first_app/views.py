d = dict
from django.shortcuts import render
from hypergen.imports import *

from contextlib import contextmanager

from hypertrek import hypertrek
from hypergen_first_app.treks import example_trek

# as_hypergen

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

    script("""
            document.addEventListener('keydown', function(event) {
                var upperKey = event.key.toUpperCase();
                if ((event.ctrlKey || event.metaKey) && event.shiftKey) {
                    if (upperKey === 'Y') {
                        event.preventDefault();
                        var previousButton = document.getElementById('previous');
                        if (previousButton) {
                            previousButton.click();
                        }
                    } else if (upperKey === 'U') {
                        event.preventDefault();
                        var nextButton = document.getElementById('next');
                        if (nextButton) {
                            nextButton.click();
                        }
                    }
                }
            });
    """)

base_template.target_id = "content"

def trek_template(trek, state, mission, as_args, as_kwargs, store):
    min_, max_, current = hypertrek.progress(trek, state)
    progress(value=current / ((max_+min_) / 2), style=d(width="100%"))
    p("On page ", current, " out of minimum ", min_, " and maximum ", max_, ".")

    inpt = mission.as_hypergen(*as_args, **as_kwargs)
    if not state["hypertrek"]["at_end"]:
        with p():
            button("Send", id_="commit", onclick=callback(post, store.uuid, inpt), autofocus=True)
    hprint(state=state)
    with p():
        if not state["hypertrek"]["at_beginning"]:
            button("<-", id_="previous", onclick=callback(bck, store.uuid))
        span(" ")
        if not state["hypertrek"]["at_end"]:
            button("->", id_="next", onclick=callback(fwd, store.uuid, inpt))

@liveview(perm=NO_PERM_REQUIRED, base_template=base_template)
def get(request):
    store = hypertrek.JsonStore()
    hprint(store.uuid)
    trek = example_trek()
    state = hypertrek.new_state(store=store)
    cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state, store=store)
    assert cmd == hypertrek.RETRY
    trek_template(trek, state, mission, as_args, as_kwargs, store)

@liveview(path="load/<slug:uuid>/", perm=NO_PERM_REQUIRED, base_template=base_template)
def load(request, uuid):
    store = hypertrek.JsonStore(uuid=uuid)
    hprint(store.uuid)
    trek = example_trek()
    state = store.get()
    state = hypertrek.rewind(trek, state, store=store)
    cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state, store=store)
    assert cmd == hypertrek.RETRY
    trek_template(trek, state, mission, as_args, as_kwargs, store)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def post(request, uuid, inpt):
    store = hypertrek.JsonStore(uuid=uuid)
    state = store.get()
    trek = example_trek()
    cmd, state, mission, (as_args, as_kwargs) = hypertrek.post(trek, state, inpt, store=store)
    if cmd == hypertrek.CONTINUE:
        state = hypertrek.forward(trek, state, store=store)
        cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state, store=store)

    trek_template(trek, state, mission, as_args, as_kwargs, store)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def bck(request, uuid):
    store = hypertrek.JsonStore(uuid=uuid)
    state = store.get()
    trek = example_trek()
    state = hypertrek.backward(trek, state, store=store)
    cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state, store=store)

    trek_template(trek, state, mission, as_args, as_kwargs, store)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def fwd(request, uuid, inpt):
    store = hypertrek.JsonStore(uuid=uuid)
    state = store.get()
    trek = example_trek()
    cmd, state, mission, (as_args, as_kwargs) = hypertrek.post(trek, state, inpt, store=store)
    if cmd == hypertrek.CONTINUE:
        state = hypertrek.forward(trek, state, store=store)
        cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state, store=store)

    trek_template(trek, state, mission, as_args, as_kwargs, store)

# as_html

def as_html(request):
    trek = example_trek()
    if request.method == "GET":
        state = hypertrek.new_state()
        cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state)
        assert cmd == hypertrek.RETRY
    elif request.method == "POST":
        state, action = loads(request.POST["state"]), request.POST["action"]
        if action in ("send", "forward"):
            inpt = hypertrek.input_from_request(trek, state, request)
            cmd, state, mission, (as_args, as_kwargs) = hypertrek.post(trek, state, inpt)
            if cmd == hypertrek.CONTINUE:
                state = hypertrek.forward(trek, state)
                cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state)
        elif action == "backward":
            state = hypertrek.backward(trek, state)
            cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state)
        else:
            raise Exception("Invalid action")

    else:
        raise Exception("Invalid method")

    min_, max_, current = hypertrek.progress(trek, state)
    progress = current / ((max_+min_) / 2)
    return render(
        request, "hypergen_first_app/trek_template.html", {
            "min": min_,
            "max": max_,
            "current": current,
            "progress": progress,
            "mission_html": mission.as_html(*as_args, **as_kwargs),
            "state": dumps(state, indent=4),
        })
