from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, forms as auth_forms
from registration.utils import generate_random_username

class RegistrationForm(auth_forms.UserCreationForm):
    """Extends the standard Django user creation form that supplies a few more
    robust defaults.

    .. note::

        To make it easier to manage registration vs. account management, this
        form should not be used for existing users to manage their accounts as
        performs "new user" operations that may override existing user
        information.

    """

    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput)
    last_name = forms.CharField(label=_('Last Name'), widget=forms.TextInput)
    email = forms.EmailField(widget=forms.TextInput(attrs={'type': 'email'}))

    class Meta(object):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_('An account is already registered with this email address.'))


class EmailOnlyRegistrationForm(RegistrationForm):
    # override the UserCreationForm field
    username = forms.CharField(required=False)

    class Meta(object):
        model = User
        fields = ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super(EmailOnlyRegistrationForm, self).save(commit=False)
        user.username = generate_random_username()
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(auth_forms.AuthenticationForm):
    email = forms.CharField(label=_('Email'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            # this is not a mistake.. Django assumes username will always be
            # used, but the auth backend accepts an email address
            self.user_cache = authenticate(username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_('Please enter a correct email '
                    'and password. Note that both fields are case-sensitive.'))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_('This account is not active.'))
        self.check_for_test_cookie()
        return self.cleaned_data


class ModerationForm(forms.Form):
    status = forms.CharField()
    comment = forms.CharField(widget=forms.Textarea, required=False)
