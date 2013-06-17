import re
import random

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns, url

from registration.user import User

USERNAME_LEN_MIN = 10 ** 10
USERNAME_LEN_MAX = 30 ** 10

def generate_random_username(attempts=10):
    qs = User.objects.all()
    r = random.SystemRandom()

    for i in xrange(attempts):
        username = str(r.randint(USERNAME_LEN_MIN, USERNAME_LEN_MAX))

        # ensure this alias is not already taken
        if not qs.filter(username=username).exists():
            return username

    raise StandardError('max attempts have been reached (n={0})'.format(attempts))

def validate_password(password, length):
    "Validates the given password."
    if len(password) < length:
        raise forms.ValidationError(_('The password provided must be at '
            'least {0} characters.'.format(length)))

    cnt = 0
    # contain lowercase letters?
    if re.search('[a-z]+', password):
        cnt += 1
    # contain uppercase letters?
    if re.search('[A-Z]+', password):
        cnt += 1
    # contain numbers?
    if re.search('[0-9]+', password):
        cnt += 1
    # contain symbols?
    if re.search('[^a-zA-Z0-9]+', password):
        cnt += 1

    if cnt < 3:
        raise forms.ValidationError(_('This password does not meet the minimum '
            'requirements.'))


def create_urls(backend):
    return patterns('',
        url(r'^activate/complete/$', 'django.views.generic.simple.direct_to_template', {
            'template': 'registration/activation_complete.html'
        }, name='registration_activation_complete'),
    
        # Activation keys get matched by \w+ instead of the more specific
        # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
        # that way it can return a sensible "invalid key" message instead of a
        # confusing 404.
        url(r'^activate/(?P<activation_key>\w+)/$', 'registration.views.activate', {
            'backend': backend
        }, name='registration_activate'),

        url(r'^register/$', 'registration.views.register', {
            'backend': backend
        }, name='register'),
    
        url(r'^register/complete/$', 'django.views.generic.simple.direct_to_template', {
            'template': 'registration/registration_complete.html'
        }, name='registration-complete'),
        
        url(r'^register/closed/$', 'django.views.generic.simple.direct_to_template', {
            'template': 'registration/registration_closed.html'
        }, name='registration-disabled'),
    )
