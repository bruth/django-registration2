from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Python 2.7 has an importlib with import_module; for older Pythons,
# Django's bundled copy provides it.
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

REGISTRATION_BACKENDS = getattr(settings, 'REGISTRATION_BACKENDS', {
    'default': 'registration.backends.default.DefaultBackend',
    'simple': 'registration.backends.simple.SimpleBackend',
})

def get_backend(alias):
    """Return an instance of a registration backend, given the dotted
    Python import path (as a string) to the backend class.

    If the backend cannot be located (e.g., because no such module
    exists, or because the module does not contain a class of the
    appropriate name), ``django.core.exceptions.ImproperlyConfigured``
    is raised.
    """
    if not REGISTRATION_BACKENDS.has_key(alias):
        raise ImproperlyConfigured('No registration backend named "{0}"'.format(alias))

    path = REGISTRATION_BACKENDS[alias]

    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]

    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error loading registration backend {0}: "{1}"'.format(module, e))

    try:
        backend_class = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "{0}" does not define a registration backend named "{1}"'.format(module, attr))

    return backend_class()
