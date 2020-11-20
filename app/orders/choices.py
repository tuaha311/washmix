class StatusChoices:
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    MAP = {
        ACCEPTED: "Accepted",
        IN_PROGRESS: "In progress",
        COMPLETED: "Completed",
    }
    CHOICES = list(MAP.items())


class PaymentChoices:
    UNPAID = "unpaid"
    PAID = "paid"
    FAIL = "fail"

    MAP = {
        UNPAID: "Unpaid",
        PAID: "Paid",
        FAIL: "Fail",
    }
    CHOICES = list(MAP.items())
