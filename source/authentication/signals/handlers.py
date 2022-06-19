from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from authentication import utils as auth_utils
from core_utils import email_handler, utils
from source.authentication.data import ACTIVATION_URL

from . import signals


@receiver(reset_password_token_created)
def password_reset_token_created(instance, reset_password_token, *args, **kwargs):
    """
    Handle password reset tokens.

    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    """
    # send an e-mail to the user
    context = {
        "username": reset_password_token.user.username,
        "email": reset_password_token.user.email,
        "reset_password_url": f"{settings.DOMAIN}/auth/create-password/{reset_password_token.key}",
    }
    html_template = f'<html><a href="{context["reset_password_url"]}" target="blank">Reset Password</a></html>'
    subject = f"forgot password for {context['email']}"
    response = email_handler.send_email(
        ["asif.mansoori@janio.asia"],
        subject,
        context["reset_password_url"],
        html=html_template,
    )
    return response.ok


@receiver(signals.user_registered)
def handle_user_registered(instance, user, request, *args, **kwargs):
    UserActivation.send_activation_link(user)


@receiver(signals.user_activated)
def send_activation_link(instance, user, request, *args, **kwargs):
    UserActivation.send_activation_link(user)


class UserActivation:
    token_generator = default_token_generator

    @classmethod
    def send_activation_link(cls, user):
        if settings.SEND_ACTIVATION_EMAIL:
            email_to = [auth_utils.get_user_email(user)]
            context = {
                "user": user,
                "uid": utils.encode_str(user.pk),
                "token": cls.token_generator.make_token(user),
            }
            activation_url = ACTIVATION_URL.format(**context)
            email_handler.send_email(
                email_to, "Visit link to activate user", activation_url
            )
