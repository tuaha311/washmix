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
