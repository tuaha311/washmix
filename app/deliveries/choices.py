class DeliveryStatus:
    CANCELLED = "cancelled"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    MAP = {
        CANCELLED: "Cancelled",
        ACCEPTED: "Accepted",
        IN_PROGRESS: "In progress",
        COMPLETED: "Completed",
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

class PickupDays:
    MON = "1"
    TUE = "2"
    WED = "3"
    THU = "4"
    FRI = "5"
    SAT = "6"
    SUN = "7"

    PICKUP_DAYS_MAP = {
        MON: "Monday",
        TUE: "Tuesday",
        WED: "Wednesday",
        THU: "Thursday",
        FRI: "Friday",
        SAT: "Saturday",
        SUN : "Sunday"
    }
    
    CHOICES = list(PICKUP_DAYS_MAP.items())