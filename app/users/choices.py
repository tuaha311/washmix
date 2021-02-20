class ClientStarch:
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


class ClientCrease:
    ALL_PANTS = "all_pants"
    JEANS_ONLY = "jeans_only"
    MAP = {ALL_PANTS: "All Pants", JEANS_ONLY: "Jeans Only"}
    CHOICES = list(MAP.items())


class ClientDetergents:
    SCENTED = "scented"
    HYPO_ALLERGENIC = "hypo_allergenic"
    MAP = {
        SCENTED: "Scented",
        HYPO_ALLERGENIC: "Hypo-Allergenic",
    }
    CHOICES = list(MAP.items())


class EmployeePosition:
    LAUNDRESS = "laundress"
    DRIVER = "driver"
    MANAGER = "manager"
    MAP = {
        DRIVER: "Driver",
        LAUNDRESS: "Laundress",
        MANAGER: "Manager",
    }
    CHOICES = list(MAP.items())


class CustomerKind:
    INTERESTED = "interested"
    POSSIBLE = "possible"
    STORAGE = "storage"
    MAP = {
        INTERESTED: "Who interested in our services in future",
        POSSIBLE: ("Who uses only SMS orders and " "maybe will use web-application in future"),
        STORAGE: "Who interested in garment storage in our warehouse",
    }
    CHOICES = list(MAP.items())
