from datetime import datetime, timedelta

from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from registration.managers import RegistrationManager

class RegistrationProfile(models.Model):
    """A simple profile which stores an activation key for use during user
    account registration.

    Generally, you will not want to interact directly with instances of this
    model; the provided manager includes methods for creating and activating
    new accounts, as well as for cleaning out accounts which have never been
    activated.

    While it is possible to use this model as the value of the
    ``AUTH_PROFILE_MODULE`` setting, it's not recommended that you do so. This
    model's sole purpose is to store data temporarily during account
    registration and activation.
    """

    user = models.OneToOneField(User, related_name='registration',
        verbose_name=_('user'))

    activation_key = models.CharField(_('activation key'), max_length=40)

    # for moderated account registration, this denotes the user has verified
    # they account e.g. clicked on a link sent to their email address
    verified = models.BooleanField(_('verified'), default=False)

    # denotes this user has been activated from a registration's perspective.
    # note, this is independent of ``User.is_active``
    activated = models.BooleanField(_('activated'), default=False)

    # denotes the user has been moderated
    moderated = models.BooleanField(_('moderated'), default=False)

    # denotes the user has been moderated
    moderator = models.ForeignKey(User, related_name='moderated_profiles',
        null=True, verbose_name=_('moderator'))

    # the time the user was moderated
    moderation_time = models.DateTimeField(_('moderation_time'), null=True)

    objects = RegistrationManager()

    class Meta(object):
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')

    def __unicode__(self):
        return u'Registration Profile for %s' % self.user

    def save(self):
        if not self.moderation_time and self.moderated:
            self.moderation_time = datetime.now()
        super(RegistrationProfile, self).save()

    @transaction.commit_on_success
    def activate(self):
        if not self.activation_expired():
            user = self.user
            user.is_active = True
            user.save()
            self.activated = True
            self.save()
            return user

    def activation_expired(self, activation_days=None):
        """Determine whether this ``RegistrationProfile``'s activation key has
        expired, returning a boolean -- ``True`` if the key has expired.

        Key expiration is determined by a two-step process:

        1. If the user has already activated, the flag ``activated`` will be
        set to true

        2. Otherwise, the date the user signed up is incremented by the number
        of days specified in the setting ``ACCOUNT_ACTIVATION_DAYS`` (which
        should be the number of days after signup during which a user is
        allowed to activate their account); if the result is less than or equal
        to the current date, the key has expired and this method returns
        ``True``.
        """
        # this profile has already been activated
        if self.activated:
            return True

        # if this is not set or is 0, always return False (no expiration)
        if not activation_days:
            return False

        # check is this has expired given the activation days
        expiration_date = timedelta(days=activation_days)
        return self.user.date_joined + expiration_date <= datetime.now()

    # for the admin..
    activation_expired.boolean = True
