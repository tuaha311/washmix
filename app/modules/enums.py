from enum import Enum

PACKAGE_NAMES = {"PAYC": 0, "GOLD": 99, "PLATINUM": 199}


class PACKAGES(Enum):
    PAYC = "PAYC"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class Detergents(Enum):
    SCENTED = "Scented"
    HYPOALLERGENIC = "Hypo-Allergenic"


class Starch(Enum):
    NONE = "NONE"
    LIGHT = "LIGHT"
    MEDIUM = "MEDIUM"
    HEAVY = "HEAVY"


class Crease(Enum):
    ALL_PANTS = "ALL_PANTS"
    JEANS_ONLY = "JEANS_ONLY"


class AppUsers(Enum):
    POTENTIAL_USERS = "POTENTIAL_USERS"
    REGULAR_USERS = "REGULAR_USERS"
    EMPLOYEE = "EMPLOYEE"


class SignUp(Enum):
    facebook = "facebook"
    google = "google-oauth2"
    washmix = "washmix"


class CouponType(Enum):
    FIRST = "FIRST"
    PACKAGE = "PACKAGE"


class BalanceOperation(Enum):
    ADD = "add"
    DEDUCT = "deduct"
    MANUAL = "manual"