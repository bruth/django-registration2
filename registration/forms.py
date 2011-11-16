from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, forms as auth_forms
from registration.utils import validate_password, generate_random_username

MIN_PASSWORD_LENGTH = 8

class PasswordResetForm(forms.ModelForm):
    "Password reset form, intended to be used for a non-authenticated user."
    password1 = forms.CharField(label=_('Password'),
        widget=forms.PasswordInput,
        help_text=_('Passwords must be {0} characters in length and contain '
            'characters from 3 of the 4 categories: lowercase characters, '
            'uppercase characters, numbers and symbols.'.format(MIN_PASSWORD_LENGTH)))

    password2 = forms.CharField(label=_('Re-type Password'), widget=forms.PasswordInput)

    class Meta(object):
        model = User
        fields = ()

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = self.cleaned_data
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password1 != password2:
            raise forms.ValidationError('The two passwords supplied do not match')
        return cleaned_data

    def save(self, commit=True):
        self.instance.set_password(self.cleaned_data.get('password1'))
        if commit:
            self.instance.save()
        return self.instance


class PasswordChangeForm(PasswordResetForm):
    "Password change form, intended for authenticated users."
    current_password = forms.CharField(label=_('Current Password'), widget=forms.PasswordInput)

    def clean_current_password(self):
        password = self.cleaned_data.get('current_password')
        if not self.instance.check_password(password):
            raise forms.ValidationError(_('Your current password you supplied is not correct'))
        return password


class RegistrationForm(auth_forms.UserCreationForm, PasswordResetForm):
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
        email = self.cleaned_data['email']

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
        user = super(forms.ModelForm, self).save(commit=False)

        user.username = generate_random_username()
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
            self.save_m2m()
        return user


class EmailAuthenticationForm(forms.Form):
    email = forms.CharField(label=_('Email'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)

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

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(_('Your Web browser does not appear '
                'to have cookies enabled. Cookies are required for logging in.'))

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id

    def get_user(self):
        return self.user_cache


class AccountForm(PasswordChangeForm):
    "Form for updating account details of authenticated users."
    email = forms.EmailField()

    class Meta(object):
        model = User
        fields = ('email',)


class ModerationForm(forms.Form):
    status = forms.CharField()
    comment = forms.CharField(widget=forms.Textarea, required=False)
