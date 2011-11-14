from django.shortcuts import redirect
from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import permission_required

from registration import signals
from registration.backends import get_backend

def register(request, backend, template_name='registration/registration_form.html'):
    backend = get_backend(backend)

    # determine is registration is currently allowed. the ``request`` object
    # is passed which can be used to selectively disallow registration based on
    # the user-agent
    if not backend.registration_allowed(request):
        return redirect(*backend.registration_closed_redirect(request))

    form_class = backend.get_registration_form_class(request)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            user = backend.register(request, form)
            return redirect(*backend.post_registration_redirect(request, user))
    else:
        form = form_class()

    return render(request, template_name, {'form': form})

@never_cache
def verify(request, backend, template_name='registration/registration_verify.html', **kwargs):
    backend = get_backend(backend)
    profile = backend.get_profile(request, **kwargs)

    moderation_required = False
    # check to see if moderation for this profile is required and whether or
    # not it is a verified account. 
    if backend.moderation_required(profile) and not profile.verified:
        moderation_required = True
    else:
        # attempt to activate this user
        profile = backend.activate(request, profile, **kwargs)

    return render(request, template_name, {
        'profile': profile,
        'moderation_required': moderation_required,
    })

@never_cache
def moderate(request, backend, template_name='registration/registration_moderate.html', **kwargs):
    backend = get_backend(backend)
    profile = backend.get_profile(request, **kwargs)
    form_class = backend.get_moderation_form_class(request)

    if request.method == 'POST':
        form = form_class(request.POST)

        if form.is_valid():
            backend.moderate(request, form, **kwargs)
            return redirect(*backend.post_moderation_redirect(request, profile))
    else:
        form = form_class()

    return rende(request, template_name, {
        'form': form,
        'profile': profile,
    })

@permission_required('registration.change_registrationprofile')
def moderate_list(request, backend, template_name='registration/registration_moderate_list.html'):
    backend = get_backend(backend)
    profiles = backend.get_profiles(request)

    return render(request, template_name, {
        'profiles': profiles,
    })