from django.conf import settings


class WashmixEmailContext:
    instagram_url = settings.INSTAGRAM_URL
    facebook_url = settings.FACEBOOK_URL
    twitter_url = settings.TWITTER_URL
    domain = settings.DOMAIN
    phone_number = settings.PHONE_NUMBER
    laundry_address = settings.LAUNDRY_ADDRESS


washmix_context = WashmixEmailContext()
