d = dict

from functools import wraps

from toolz import curry

def mission(*, renderers, configurator):
    def _(f):
        @curry
        @wraps(f)
        def __(*args, **kwargs):
            return f(*args, **kwargs)

        __.hypertrek = d(renderers=renderers, configurator=configurator)
        return __

    return _
