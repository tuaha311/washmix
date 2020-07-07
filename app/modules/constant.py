from enum import Enum

MESSAGE_PICK_UP = 'Hi {0}, your garments will be picked at Date & Time {1} from  Address: {2}.\nThanks for using WashMix!'

MESSAGE_DROP_OFF = 'Hi {0}, your garments will be delivered at Date & Time {1} from {2}.\nThanks for using WashMix!'

WASHMIX_TEAM_ORDER_PICK = """
PICKUP
- {0}:\n
- {1}\n
- {2}\n
- {3}\n
"""

WASHMIX_TEAM_ORDER_DROPOFF = """
DROP-OFF
- {0}:\n
- {1}\n
- {2}\n
- {3}\n
"""

# Error Messages

MESSAGE_ERROR_MISSING_ADDRESS = 'For an Order, Pickup/Dropoff address is compulsory'



from rest_framework import serializers


class EnumField(serializers.ChoiceField):
    def __init__(self, enum, **kwargs):
        self.enum = enum
        kwargs['choices'] = [(e, e.value) for e in enum]
        super(EnumField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return obj.name

    def to_internal_value(self, data):
        try:
            return self.enum[data].value
        except KeyError:
            self.fail('invalid_choice', input=data)


# Package Types
PACKAGE_NAMES = {'PAYC': 0, 'GOLD': 99, 'PLATINUM': 199}


class PACKAGES(Enum):
    PAYC = 'PAYC'
    GOLD = 'GOLD'
    PLATINUM = 'PLATINUM'


# Preferences
class Detergents(Enum):
    SCENTED = 'Scented'
    HYPOALLERGENIC = 'Hypo-Allergenic'


class Starch(Enum):
    NONE = 'NONE'
    LIGHT = 'LIGHT'
    MEDIUM = 'MEDIUM'
    HEAVY = 'HEAVY'


class Crease(Enum):
    ALL_PANTS = 'ALL_PANTS'
    JEANS_ONLY = 'JEANS_ONLY'


class AppUsers(Enum):
    POTENTIAL_USERS = 'POTENTIAL_USERS'
    REGULAR_USERS = 'REGULAR_USERS'
    EMPLOYEE = 'EMPLOYEE'


class SignUp(Enum):
    facebook = 'facebook'
    google= 'google-oauth2'
    washmix = 'washmix'


class CouponType(Enum):
    FIRST = 'FIRST'
    PACKAGE = 'PACKAGE'
