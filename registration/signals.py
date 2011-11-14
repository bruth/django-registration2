from django.dispatch import Signal

# A new user has registered.
user_registered = Signal(providing_args=['user', 'request', 'backend'])

# A new user has verified their registration.
user_verified = Signal(providing_args=['user', 'request', 'backend'])

# A user has activated his or her account.
user_activated = Signal(providing_args=['user', 'request', 'backend'])

# A user has been moderated.
user_moderated = Signal(providing_args=['user', 'request', 'backend'])
