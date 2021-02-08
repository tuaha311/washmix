class InvoicePurpose:
    CREDIT = "credit"
    SUBSCRIPTION = "subscription"
    BASKET = "basket"
    PICKUP = "pickup"
    DROPOFF = "dropoff"
    MAP = {
        CREDIT: "Credit by WashMix",
        SUBSCRIPTION: "Subscription purchase",
        BASKET: "Items in basket",
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


class WebhookKind:
    SUBSCRIPTION = "subscription"
    SUBSCRIPTION_WITH_CHARGE = "subscription_with_charge"
    REFILL_WITH_CHARGE = "refill_with_charge"
    MAP = {
        SUBSCRIPTION: "Advantage Program subscription purchase",
        SUBSCRIPTION_WITH_CHARGE: "Subscription purchase with charge for POS order",
        REFILL_WITH_CHARGE: "One time refill with charge for POS order",
    }
    CHOICES = list(MAP.items())
