
REGISTRY = {}
_future_dependencies = {}
_future_optionals = {}


class UnresolvableDependencyException(Exception):
    def __init__(self, name):
        msg = 'Unregistered dependency: %s' % name
        super(UnresolvableDependencyException, self).__init__(msg)


def provider(name):
    def wrapped(cls):

        def wrapper(init):
            def __wrapper_init__(self, *args, **kwargs):
                init(self, *args, **kwargs)
                REGISTRY[name] = self

                resolve_future_dependencies(name)
            return __wrapper_init__

        cls.__init__ = wrapper(cls.__init__)
        return cls
    return wrapped


def resolve_future_dependencies(provider_name=None):
    if provider_name:
        # A provider was registered, so take care of any objects depending on
        # it.
        targets = _future_dependencies.pop(provider_name, [])
        targets.extend(_future_optionals.pop(provider_name, []))

        for target in targets:
            setattr(target, provider_name, REGISTRY[provider_name])

        return

    # Resolve optional dependencies, raises UnresolvableDependencyException if
    # there's no provider registered.
    try:
        for dependency, targets in _future_dependencies.iteritems():
            if dependency not in REGISTRY:
                raise UnresolvableDependencyException(dependency)

            for target in targets:
                setattr(target, dependency, REGISTRY[dependency])
    finally:
        _future_dependencies.clear()


def requires(*dependencies):
    def wrapper(self, *args, **kwargs):
        self.__wrapped_init__(*args, **kwargs)
        _process_dependencies(self)

    def wrapped(cls):
        existing_dependencies = getattr(cls, '_dependencies', set())
        cls._dependencies = existing_dependencies.union(dependencies)
        if not hasattr(cls, '__wrapped_init__'):
            cls.__wrapped_init__ = cls.__init__
            cls.__init__ = wrapper
        return cls

    return wrapped


def _process_dependencies(obje):
    def process(obj, attr_name, unresolved_in_out):
        for dependency in getattr(obj, attr_name, []):
            if dependency not in REGISTRY:
                # We don't know about this dependency, so save it for later.
                unresolved_in_out.setdefault(dependency, []).append(obj)
                continue

            setattr(obj, dependency, REGISTRY[dependency])

    process(obje, '_dependencies', _future_dependencies)
