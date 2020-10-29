class Status:
    UNPAID = "unpaid"
    PAID = "paid"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    MAP = {
        UNPAID: "Unpaid",
        PAID: "Paid",
        IN_PROGRESS: "In progress",
        COMPLETED: "Completed",
    }
    CHOICES = list(MAP.items())
