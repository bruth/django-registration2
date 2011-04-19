from django.conf import settings
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site, RequestSite

from registration import signals
from registration.forms import RegistrationForm, ModerationForm
from registration.models import RegistrationProfile, ALREADY_ACTIVATED

class DefaultBackend(object):

    def _send_registration_email(self, request, profile):
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
            'moderated': self.moderation_required(request, profile),
            'expiration_days': self.get_activation_days(request),
        })

        profile.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

    def _send_moderator_email(self, request, profile):
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
            'expiration_days': self.get_activation_days(request),
        })

        # send an email to all account moderators
        moderators = (x[1] for x in self.get_moderators(request))
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, moderators)

    def _send_acceptance_email(self, request, profile, **context):
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

    def get_profile(self, request, activation_key):
        try:
            return RegistrationProfile.objects.select_related('user').get(activation_key=activation_key)
        except RegistrationProfile.DoesNotExist:
            pass

    def get_profiles(self, request, **kwargs):
        return RegistrationProfile.objects.filter(**kwargs)

    def register(self, request, form):
        cleaned_data = form.cleaned_data
        username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        user = RegistrationProfile.objects.create_inactive_user(username,
            email, password, site)

        self._send_registration_email(request, user.registration)

        return user

    def activate(self, request, activation_key):
        """
        Given an an activation key, look up and activate the user
        account corresponding to that key (if possible).

        After successful activation, the signal
        ``registration.signals.user_activated`` will be sent, with the
        newly activated ``User`` as the keyword argument ``user`` and
        the class of this backend as the sender.

        """
        activated = RegistrationProfile.objects.activate_user(activation_key)
        if activated:
            signals.user_activated.send(sender=self.__class__, user=activated,
                request=request)

        return activated

    def verify(self, request, activation_key):
        """
        Given an activation key, mark the account as being verified for
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
                request=request)

            self._send_moderator_email(request, profile)

        return profile

    @transaction.commit_on_success
    def moderate(self, request, form, activation_key, **kwargs):
        cleaned_data = form.cleaned_data

        # mark the registration profile as active
        profile = self.get_profile(request, activation_key)

        if not profile:
            return

        profile.activation_key = ALREADY_ACTIVATED
        profile.save()

        if cleaned_data['status'].lower() == 'accept':
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
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def moderation_required(self, request, profile):
        "Indicate whether account moderation is enabled."
        return getattr(settings, 'ACCOUNT_MODERATION', False)

    def get_moderators(self, request):
        "Returns a tuple of moderators."
        return getattr(settings, 'ACCOUNT_MODERATORS', ())

    def get_activation_days(self, request):
        "Returns the number of days allowed for activation"
        return getattr(self, 'ACCOUNT_ACTIVATION_DAYS', None)

    def get_registration_form_class(self, request):
        """
        Return the default form class used for user registration.
        """
        return RegistrationForm

    def get_moderation_form_class(self, request):
        return ModerationForm

    def post_registration_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        user registration.
        """
        return ('registration_complete', (), {})

    def post_activation_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        account activation.
        """
        return ('registration_activation_complete', (), {})

    def post_moderation_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful account
        moderation.
        """
        return ('registration_moderate_list', (), {})
