from django.conf import settings
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site, RequestSite

from registration import signals
from registration.forms import RegistrationForm, ModerationForm
from registration.models import RegistrationProfile


class DefaultBackend(object):
    def get_profile(self, request, activation_key):
        "Returns a single profile by ``activation_key``."
        try:
            return self.get_profiles(request).get(activation_key=activation_key)
        except RegistrationProfile.DoesNotExist:
            pass

    def get_profiles(self, request, **kwargs):
        "Returns a QuerySet of registration profiles."
        return RegistrationProfile.objects.select_related('user').filter(**kwargs)

    def register(self, request, form):
        "Post-form validation registration logic."
        cleaned_data = form.cleaned_data
        username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        user = RegistrationProfile.objects.create_inactive_user(username,
            email, password, site)

        self._send_registration_email(request, user.registration)
        signals.user_registered.send(sender=self.__class__, user=user,
            request=request, backend=self)

        return user

    def activate(self, request, activation_key):
        """Given an an activation key, look up and activate the user account
        corresponding to that key (if possible).

        After successful activation, the signal ``user_activated`` will be
        sent, with the newly activated ``User`` as the keyword argument
        ``user`` and the class of this backend as the sender.
        """
        profile = self.get_profile(request, activation_key)

        if profile and profile.activate():
            signals.user_activated.send(sender=self.__class__, user=profile.user,
                request=request, backend=self)

        return profile

    def verify(self, request, activation_key):
        """Given an activation key, mark the account as being verified for
        moderation. Send an email to all account moderators on the first
        occurence.

        The status of the verification is returned which denotes whether the
        verification was successful or the account has already been verified.
        """
        profile = self.get_profile(request, activation_key)

        if profile and not profile.verified:
            # marked as verified
            profile.verified = True
            profile.save()

            # send verification signal
            signals.user_verified.send(sender=self.__class__, user=profile.user,
                request=request, backend=self)

            self._send_moderator_email(request, profile)

        return profile

    @transaction.commit_on_success
    def moderate(self, request, form, activation_key, **kwargs):
        cleaned_data = form.cleaned_data

        # mark the registration profile as active
        profile = self.get_profile(request, activation_key)

        if not profile:
            return

        profile.moderated = True
        profile.save()

        if cleaned_data['status'].lower() == 'approve':
            # mark the user as active
            profile.user.is_active = True
            profile.user.save()

        self._send_acceptance_email(request, profile, **cleaned_data)

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.

        """
        return getattr(settings, 'ACCOUNT_REGISTRATION_OPEN', True)

    def moderation_required(self, request, profile):
        "Indicate whether account moderation is enabled."
        return getattr(settings, 'ACCOUNT_MODERATION', False)

    def get_moderators(self, request):
        "Returns a tuple of moderators."
        return getattr(settings, 'ACCOUNT_MODERATORS', settings.MANAGERS)

    def get_activation_days(self, request):
        "Returns the number of days allowed for activation"
        return getattr(self, 'ACCOUNT_ACTIVATION_DAYS', 0)

    def get_registration_form_class(self, request):
        "Return the form class used for user registration."
        return RegistrationForm

    def get_moderation_form_class(self, request):
        "Return the form class used for user moderation."
        return ModerationForm

    def post_registration_redirect(self, request, user):
        "Return the ``reverse`` arguments for post-registration."
        return 'registration_complete', (), {}

    def post_activation_redirect(self, request, user):
        "Return the ``reverse`` arguments for post-activation."
        return 'registration_activation_complete', (), {}

    def post_moderation_redirect(self, request, user):
        "Return the ``reverse` arguments for post-moderation."
        return 'registration_moderate_list', (), {}


def send_registration_email(backend, request, profile, **kwargs):
    # get the current site
    if Site._meta.installed:
        site = Site.objects.get_current()
    else:
        site = RequestSite(request)

    # send a new user registration email explaining the next steps
    subject = render_to_string('registration/registration_subject.txt', {
        'site': site
    })
    # no newlines
    subject = ''.join(subject.splitlines())

    message = render_to_string('registration/registration_email.txt', {
        'site': site,
        'profile': profile,
        'moderated': backend.moderation_required(request, profile),
        'expiration_days': backend.get_activation_days(request),
    })

    profile.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

def send_moderator_email(request, profile, backend):
    # get the current site
    if Site._meta.installed:
        site = Site.objects.get_current()
    else:
        site = RequestSite(request)

    # send a new user registration email explaining the next steps
    subject = render_to_string('registration/moderator_subject.txt', {
        'site': site
    })

    # no newlines
    subject = ''.join(subject.splitlines())

    message = render_to_string('registration/moderator_email.txt', {
        'site': site,
        'profile': profile,
        'expiration_days': backend.get_activation_days(request),
    })

    # send an email to all account moderators
    moderators = (x[1] for x in backend.get_moderators(request))
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, moderators)

def send_acceptance_email(request, profile, **context):
    # get the current site
    if Site._meta.installed:
        site = Site.objects.get_current()
    else:
        site = RequestSite(request)

    # send a new user registration email explaining the next steps
    subject = render_to_string('registration/acceptance_subject.txt', {
        'site': site
    })

    # no newlines
    subject = ''.join(subject.splitlines())

    context.update({
        'site': site,
        'profile': profile,
    })

    message = render_to_string('registration/acceptance_email.txt', context)

    profile.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)