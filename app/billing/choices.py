class Purpose:
    SUBSCRIPTION = "subscription"
    ORDER = "order"
    DELIVERY = "delivery"
    MAP = {
        SUBSCRIPTION: "Subscription purchase",
        ORDER: "Order processing payment",
        DELIVERY: "Payment for delivery",
    }
    CHOICES = list(MAP.items())
