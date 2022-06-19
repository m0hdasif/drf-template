def get_user_email(user):
    """Get user email from user model."""
    email_field_name = get_user_email_field_name(user)
    return getattr(user, email_field_name, None)


def get_user_email_field_name(user):
    """Find email field name set in the model."""
    return user.get_email_field_name()
