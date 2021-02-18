from djoser.compat import get_user_email as djoser_get_user_email


def cleanup_email(email: str) -> str:
    """
    Email cleanup function.
    """

    email = email.strip().lower()

    return email


def get_custom_user_email(user) -> str:
    """
    Changed implementation of `get_user_email` djoser.
    """

    email = djoser_get_user_email(user)
    clean_email = cleanup_email(email)

    return clean_email
