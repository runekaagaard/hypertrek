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
