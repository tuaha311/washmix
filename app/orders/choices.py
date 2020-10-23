class Status:
    ACCEPTED = "accepted"
    PAID = "paid"
    COMPLETED = "completed"

    MAP = {
        ACCEPTED: "Accepted",
        PAID: "Paid",
        COMPLETED: "Completed",
    }
    CHOICES = list(MAP.items())
