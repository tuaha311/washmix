from django.conf import settings
from django.contrib.auth.models import User

import requests
from oauth2_provider.models import AccessToken


def convert_to_auth_token(client_id, client_secret, backend, token):
    """
    given a previously generated access_token use the django-rest-framework-social-oauth2
    endpoint `/convert-token/` to authenticate the user and return a django auth token
    :param client_id: from OauthToolkit application
    :param client_secret: from OauthToolkit application
    :param backend: authentication backend to user ('github', 'facebook', etc)
    :param token: access token generated from the backend - github
    :return: django auth token
    """
    params = {
        "grant_type": "convert_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "backend": backend,
        "token": token,
    }
    response = requests.post("{}/auth/convert-token/".format(settings.API_URL), params=params)
    return response.json()


def get_user_from_token(django_auth_token):
    """
    Retrieve the user object given an access token
    :param django_auth_token: Oauthtoolkit access TOKEN
    :return: user object
    """
    return User.objects.get(
        id=AccessToken.objects.get(token=django_auth_token["access_token"]).user_id
    )


def get_user_by_email(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None
