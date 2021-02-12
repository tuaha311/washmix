from django.conf import settings


def is_advantage_program(name: str) -> bool:
    """
    Checks client's subscription includes in Advantage Program
    """

    in_advantage_prorgam = name in [settings.GOLD, settings.PLATINUM]

    return in_advantage_prorgam
