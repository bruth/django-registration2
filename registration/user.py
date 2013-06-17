# Make sure the proper Django user model is stored in the User class
# Use get_user_model() for Django >= 1.5, use django.contrib.auth.models.User for Django < 1.5,
# and always store the proper class in registration.models.User
try:
    # For Django >= 1.5, use get_user_model() and store result User
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    # Django < 1.5, load User from registration.models
    from django.contrib.auth.models import User
