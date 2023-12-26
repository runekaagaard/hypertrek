d = dict

from functools import wraps

from toolz import curry

def mission(*, concerns, configurator, pageno):
    hypertrek = d(concerns=concerns, configurator=configurator, pageno=pageno)
    def _(f):
        f.hypertrek = hypertrek

        @curry
        @wraps(f)
        def __(*args, **kwargs):
            f.hypertrek = hypertrek
            return f(*args, **kwargs)

        __.hypertrek = hypertrek
        return __

    return _
