class Starch:
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    MAP = {
        NONE: "None",
        LIGHT: "Light",
        MEDIUM: "Medium",
        HEAVY: "Heavy",
    }
    CHOICES = list(MAP.items())


class Crease:
    ALL_PANTS = "all_pants"
    JEANS_ONLY = "jeans_only"
    MAP = {ALL_PANTS: "All Pants", JEANS_ONLY: "Jeans Only"}
    CHOICES = list(MAP.items())


class Detergents:
    SCENTED = "scented"
    HYPO_ALLERGENIC = "hypo_allergenic"
    MAP = {
        SCENTED: "Scented",
        HYPO_ALLERGENIC: "Hypo-Allergenic",
    }
    CHOICES = list(MAP.items())


class Position:
    LAUNDRESS = "laundress"
    DRIVER = "driver"
    MANAGER = "manager"
    MAP = {
        DRIVER: "Driver",
        LAUNDRESS: "Laundress",
        MANAGER: "Manager",
    }
    CHOICES = list(MAP.items())


class Kind:
    INTERESTED = "interested"
    POSSIBLE = "possible"
    MAP = {
        INTERESTED: "Who interested in our services in future",
        POSSIBLE: ("Who uses only SMS orders and " "maybe will use web-application in future"),
    }
    CHOICES = list(MAP.items())
