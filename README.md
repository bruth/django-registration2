# django-registration2

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/bruth/django-registration2/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

## Install

```bash
pip install django-registration2
```

## Setup

Add `registration` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    'django.contrib.auth',
    'registration',
)
```

Add `registration.urls` to your project's urls.py:

```python
urlpatterns = patterns('',
    ...
    url(r'^', 'registration.urls')),
)
```

Run [South](http://south.readthedocs.org) migrations (if installed):

```python
python manage.py migrate registration
```

Otherwise run `syncdb`:

```python
python manage.py syncdb
```

## Settings

Registration is handled by a _backend_ which is a class composed of various
methods for performing each step in the registration process. In most cases
the default behavior is suitable, but for convenience a few settings are
available to customize a few common scenarios.

### REGISTRATION_OPEN

A boolean which determines whether users can register or not. Default is `True`

### REGISTRATION_MODERATION

A boolean which defines whether or not users will be moderated before
completing their registration. Default is `False`

### REGISTRATION_MODERATORS

A tuple of name/email pairs (like `ADMINS` or `MANAGERS`) whom will be notified
of newly registered users. Defaults to `MANAGERS`

### REGISTRATION_ACTIVATION_DAYS

An integer of the number of days an account activation link is valid. Users
receive one in their email after they sign up to verify their email address
is valid. Default is `0` (no time limit)

## Signals

A few signals are exposed to notify when various events occurs. All signals
provide the following arguments:

- `user` - The new user instance
- `request` - The request instance used during registration
- `backend` - The registration backend used for registration

### `user_registered`

Sent when a user registers.

### `user_verified`

Sent when a user verifies their email address using the verification link they
receive via email. This occurs only for registration that is moderated since
moderators will not receive notice of new registrations unless they verify
their email address.

### `user_activated`

Sent when a user verifies their account using the verification link they
receive via email. This applies to non-moderated registrants.

### `user_moderated`

Sent when a moderator has moderated a user's registration (pass or fail).

## Backends

Multiple backends are supported which may be necessary to handle different
registration methods for different kinds of users.

```python
REGISTRATION_BACKENDS = {
    'default': 'registration.backends.default.Backend',
    'other': 'myapp.backends.MyBackend',
}
```


