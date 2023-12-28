from hypergen.imports import *

from contextlib import contextmanager

from hypertrek import trek
from hypergen_first_app.hypertrek import poc_trek

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

@contextmanager
def collect():
    from hypergen.imports import context, input_, select, textarea

    result = {}

    class Collector():
        @contextmanager
        def wrap_element_init(self, element, children, attrs):
            print(type(element), children, attrs)
            yield

    collector = Collector()
    context.hypergen.plugins.append(collector)
    yield result
    # TODO: remove collector from plugins.

@liveview(perm=NO_PERM_REQUIRED, base_template=base_template)
def show_trek(request):
    poc, state = trek.init(poc_trek)
    cmd, state, concerns = trek.get(poc, state)
    inpt = concerns["rendering"]["hypergen"]()

    button("Next", id_="next", onclick=callback(commit_mission, state, inpt))
    hprint(state=state)

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def commit_mission(request, state, inpt):
    poc = poc_trek()
    cmd, state, concerns = trek.post(poc, state, inpt)
    if cmd == trek.CONTINUE:
        is_done, state = trek.forward(poc, state)
        cmd, state, concerns = trek.get(poc, state)

    inpt = concerns["rendering"]["hypergen"]()
    button("Next", id_="next", onclick=callback(commit_mission, state, inpt))

    hprint(state=state, inpt=inpt)
