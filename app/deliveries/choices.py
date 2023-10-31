class DeliveryStatus:
    CANCELLED = "cancelled"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    IN_STORE_DROPOFF = "in_store_dropoff"
    IN_STORE_PICKUP = "in_store_pickup"

    MAP = {
        CANCELLED: "Cancelled",
        ACCEPTED: "Accepted",
        IN_PROGRESS: "In progress",
        COMPLETED: "Completed",
        NO_SHOW: "No Show",
        IN_STORE_DROPOFF: "In Store: dropoff",
        IN_STORE_PICKUP: "In Store: pickup",
    }
    CHOICES = list(MAP.items())


class DeliveryKind:
    PICKUP = "pickup"
    DROPOFF = "dropoff"

    MAP = {
        PICKUP: "Pickup",
        DROPOFF: "Dropoff",
    }
    CHOICES = list(MAP.items())


class WeekDays:
    MON = "1"
    TUE = "2"
    WED = "3"
    THU = "4"
    FRI = "5"
    SAT = "6"
    SUN = "7"

    WEEK_DAYS_MAP = {
        MON: "Monday",
        TUE: "Tuesday",
        WED: "Wednesday",
        THU: "Thursday",
        FRI: "Friday",
        SAT: "Saturday",
        SUN: "Sunday",
    }

    CHOICES = list(WEEK_DAYS_MAP.items())
