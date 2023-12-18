from hypergen.imports import *
from hypertrek.imports import *

from myapp.treks import *

@liveview(perm=NO_PERM_REQUIRED, base_template=base_template)
def myview(request):
    mission = trek_next(mytrek, state=None, inpt=None)
    raw(mission.side_effects.html())

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def myview_next(request, state, inpt):
    mission = trek_next(mytrek, state=state, inpt=inpt)
    raw(mission.side_effects.html())

@action(perm=NO_PERM_REQUIRED, base_template=base_template)
def myview_prev(request, state, inpt):
    mission = trek_prev(mytrek, state=state, inpt=inpt)
    raw(mission.side_effects.html())
