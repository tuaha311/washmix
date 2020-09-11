# Release Notes

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