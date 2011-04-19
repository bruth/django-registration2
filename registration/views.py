from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from registration import signals
from registration.backends import get_backend
from registration.models import RegistrationProfile

def register(request, backend, template_name='registration/registration_form.html'):
    backend = get_backend(backend)

    # determine is registration is currently allowed. the ``request`` object
    # is passed which can be used to selectively disallow registration based on
    # the user-agent
    if not backend.registration_allowed(request):
        to, args, kwargs = backend.registration_closed_redirect(request)
        return redirect(to, *args, **kwargs)

    form_class = backend.get_registration_form_class(request)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)

        if form.is_valid():
            # only if the form is valid, do we pass the local context to the
            # backend for processing. since there are no assumptions made here,
            # the backend should implement all necessary registration logic.
            # the return value should be the registration profile for the new
            # user (or None if it failed)
            user = backend.register(request, form)

            # send signal after the backend-specific registration has occurred
            signals.user_registered.send(sender=backend.__class__, request=request,
                user=user)

            # once registration is complete (or failed), we redirect to prevent
            # re-submission
            to, args, kwargs = backend.post_registration_redirect(request, user)
            return redirect(to, *args, **kwargs)
    else:
        form = form_class()

    return render_to_response(template_name, {
        'form': form
    }, context_instance=RequestContext(request))

def activate(request, backend, template_name='registration/activate.html', **kwargs):
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

    return render_to_response(template_name, {
        'profile': profile,
        'moderation_required': moderation_required,
    }, context_instance=RequestContext(request))

def verify(request, backend, template_name='registration/registration_verify.html', **kwargs):
    backend = get_backend(backend)
    verified = backend.verify(request, **kwargs)

    return render_to_response(template_name, {
        'verified': verified,
    }, context_instance=RequestContext(request))


def moderate(request, backend, template_name='registration/registration_moderate.html', **kwargs):
    backend = get_backend(backend)

    profile = backend.get_profile(request, **kwargs)
    form_class = backend.get_moderation_form_class(request)

    if request.method == 'POST':
        form = form_class(request.POST)

        if form.is_valid():
            # perform post-moderation steps
            backend.moderate(request, form, **kwargs)

            to, args, kwargs = backend.post_moderation_redirect(request, profile)
            return redirect(to, *args, **kwargs)

    else:
        form = form_class()

    return render_to_response(template_name, {
        'form': form,
        'profile': profile,
    }, context_instance=RequestContext(request))


def moderate_list(request, backend, template_name='registration/registration_moderate_list.html'):
    backend = get_backend(backend)
    profiles = backend.get_profiles(request)

    return render_to_response(template_name, {
        'profiles': profiles,
    }, context_instance=RequestContext(request))
