import re
import random

from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.hashcompat import sha_constructor

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class RegistrationManager(models.Manager):
    """Custom manager for the ``RegistrationProfile`` model.

    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.
    """
    def activate_user(self, activation_key):
        """Validate an activation key and activate the corresponding
        ``User`` if valid.

        If the key is valid and has not expired, return the ``User``
        after activating.

        If the key is not valid or has expired, return ``False``.

        If the key is valid but the ``User`` is already active,
        return ``False``.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return

            return profile.activate()

    def create_profile(self, user):
        """Create a ``RegistrationProfile`` for a given ``User``, and return
        the ``RegistrationProfile``.

        The activation key for the ``RegistrationProfile`` will be a SHA1 hash,
        generated from a combination of the ``User``'s username and a random
        salt.
        """
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        username = user.username

        if isinstance(username, unicode):
            username = username.encode('utf-8')

        activation_key = sha_constructor(salt+username).hexdigest()
        return self.create(user=user, activation_key=activation_key)

    @transaction.commit_on_success
    def create_inactive_user(self, username, email, password, site, send_email=True):
        """Create a new, inactive ``User``, generate a
        ``RegistrationProfile`` and email its activation key to the
        ``User``, returning the new ``User``.

        By default, an activation email will be sent to the new
        user. To disable this, pass ``send_email=False``.

        """
        user = User.objects.create_user(username, email, password)
        user.is_active = False
        user.save()

        registration_profile = self.create_profile(user)

        if send_email:
            registration_profile.send_activation_email(site)

        return user


