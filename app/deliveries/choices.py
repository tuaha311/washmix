class Status:
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


class Kind:
    PICKUP = "pickup"
    DROPOFF = "dropoff"

    MAP = {
        PICKUP: "Pickup",
        DROPOFF: "Dropoff",
    }
    CHOICES = list(MAP.items())
