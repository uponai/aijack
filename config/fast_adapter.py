from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError

class AccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        Overrides the default username population to always use the email.
        """
        from allauth.account.utils import user_email, user_username

        email = user_email(user)
        if email:
            user_username(user, email)
