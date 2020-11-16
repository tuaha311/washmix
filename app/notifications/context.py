from django.conf import settings


class WashmixEmailContext:
    instagram_url = settings.INSTAGRAM_URL
    facebook_url = settings.FACEBOOK_URL
    twitter_url = settings.TWITTER_URL
    domain = settings.DOMAIN
    phone_number = settings.PHONE_NUMBER


email_context = WashmixEmailContext()
