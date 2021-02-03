class InvoicePurpose:
    CREDIT = "credit"
    SUBSCRIPTION = "subscription"
    POS = "pos"
    REFILL = "refill"
    BASKET = "basket"
    PICKUP = "pickup"
    DROPOFF = "dropoff"
    MAP = {
        CREDIT: "Credit by WashMix",
        SUBSCRIPTION: "Subscription purchase",
        POS: "POS",
        REFILL: "One time refill",
        BASKET: "Order processing payment",
        PICKUP: "Pickup delivery",
        DROPOFF: "Dropoff delivery",
    }
    CHOICES = list(MAP.items())


class InvoiceDiscountBy:
    PERCENTAGE = "percentage"
    AMOUNT = "amount"
    MAP = {
        PERCENTAGE: "Discount by percentage",
        AMOUNT: "Discount by amount",
    }
    CHOICES = list(MAP.items())


class InvoiceKind:
    DEBIT = "debit"
    CREDIT = "credit"
    MAP = {
        DEBIT: "Debit",
        CREDIT: "Credit",
    }
    CHOICES = list(MAP.items())


class InvoiceProvider:
    STRIPE = "stripe"
    COUPON = "coupon"
    CREDIT_BACK = "credit_back"
    WASHMIX = "washmix"
    MAP = {
        STRIPE: "Stripe",
        COUPON: "Coupon",
        CREDIT_BACK: "Credit back",
        WASHMIX: "WashMix",
    }
    CHOICES = list(MAP.items())
