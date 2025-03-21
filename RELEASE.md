# Release Notes

## v1.7 (09.11.2020)
* Client.billing_address changed from `ForeignKey` to `JSONField`
* Added `Customer.address`, `Customer.full_name` fields
* Added `credit_back`, `dollar_credit_back` on OrderContainer
* Added REST API permissions:
  - `IsClient`
  - `IsEmployee`
* URL namespace changes:
  - `client` added
  - `driver` added
  - `pos` added
  - `v1.0` removed
* Added `Order.coupon`, `Order.subscription`
* Changed implementation of services:
  - `SubscriptionService`
  - `OrderService`
  - `CouponService`
  - `BasketService`
* Migrations regenerated
* `api` subpackage reorganization
* Added new endpoint `/pos/requests/choose/`
* Update Twilio Flex integration
* Added new Customer kind - `STORAGE`
* Added new containers:
  - `DeliveryContainer`
  - `RequestContainer`
* Added `TwilioFlexOnlineWorkersWebhookView`
* Added new templates for admin


## v1.6 (26.10.2020)
* Added `v1` views, serializer per application
* `URLconf`'s now moved into applications
* Rename `ChekoutView` to more semantic:
  - `OrderCheckoutView`
  - `SubscriptionCheckoutView`
  - `WelcomeCheckoutView`
* `StripeWebhookView`
* Added `Request` model
* Added `RequestService`
* Added amount calculation containers:
  - `BaseAmountContainer`
  - `OrderContainer`
  - `BasketContainer`
  - `QuantityContainer`
  - `RequestContainer`
* Added prepaid balance charging logic
* Added concrete `.charge` method implementation for:
  - `PaymentService`
  - `SubscriptionService`
  - `OrderService`
* Update Twilio Flex Flow JSON
* Update Model Architecture doc


## v1.5 (09.10.2020)
* Added more phone validation
* Added exception handling in body for Twilio
* Added new scheduler service for periodic tasks
* Move from script to fixtures to load initial data
* Added credit back logic for every quarter:
  - New task `accrue_credit_back_every_3_month`
* Added recurring pickup logic:
  - New `Schedule` model
  - `/api/v1.0/schedules/` endpoint
  - New task `create_recurring_delivery_every_day`
* Added task idempotency implementation
* Move `Package`, `Subscription` into `subscriptions` application
* Added new services:
  - `PaymentService`
  - `InvoiceService`
  - `CardService`
  - `DiscountService`


## v1.4 (25.09.2020)
* Added Twilio integration
* Added Twilio webhooks
* Added docs folder with following content:
  - Model architecture diagram (models_architecture.drawio)
  - Twilio flow for importing in JSON format (twilio_import_flow.json)
  - Twilio scenario flowcart (twilio_scenario_flowchart.drawio)
* Added business days calculation
* Added test cases for calculation functions and all related stuff
* Added some methods on DeliveryService
* Added models:
  - `Basket` for storing quantity of items in shopping basket
  - `Quantity` intermediate model that shows how many items in shopping basket
* Re-implemented `Order` model
* Added BasketService
* Added basic basket operations:
  - `/api/v1.0/basket/`
  - `/api/v1.0/basket/change_item/`
  - `/api/v1.0/basket/clear/`
  - `/api/v1.0/checkout/`
  

## v1.3 (11.09.2020)
* Added Coupon, Delivery models
* Finished Invoice, Transaction logic
* Added welcome email template
* Implemented logic of CouponHolder
* Business logic moved into `services` packages
* Implemented CheckoutService
* Implemented ChooseService
* Implemented PaymentService
* Implemented SignupService
* MainAttributeMixin transformed into MainAttributeService
* Implemented Package cloning into Subscription
* Fully implemented StripeHelper
* Added docker-entrypoint.sh cmd argument handling
* Move some views and serializers from `api` into applications
* Added `security` entity and response schema improvements for OpenAPI
* Added Stripe webhook implementation


## v1.2 (28.08.2020)
* Move from default DRF's OpenAPI library to drf-yasg
* Change static path from /static/ -> /assets/
* Added CouponHolder (business logic holder for apply coupons)
* Added PackageHandler (business logic holder for package choose)
* Added StripeHelper (wrapper around Stripe)
* Added Invoice, Subscription models
* Move data from management-commands into initial_data
* Added meta-class for behavior creation
* Move from USD to CENTS
* Added basic implementation for dramatiq
* Added welcome scenario endpoints 


## v1.1 (14.08.2020)
* Added OpenAPI documentation
* Added integration with SendGrid
* Added authorization and authentication API
* Added account reset API
* Added packages, locations, services API
* Architecture refactoring
* Model refactoring
* Code refactoring
* Dependency update and cleanup
* Added pre-commit hooks