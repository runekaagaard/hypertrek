d = dict

from functools import wraps

from toolz import curry

def mission(*, concerns, configurator, progress):
    hypertrek = d(concerns=concerns, configurator=configurator, progress=progress)
    def _(f):
        f.hypertrek = hypertrek

        @curry
        @wraps(f)
        def __(*args, **kwargs):
            return f(*args, **kwargs)

        __.hypertrek = hypertrek
        return __

    return _
