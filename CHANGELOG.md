# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- [amazon/order-close] Amazon Order Close - initial release
### Security
- [common/order-pre-processor] Removing the API key details from docker compose
- [amazon/pull-orders] Removing the API key details from docker compose

## [0.0.4] - 2023-08-25

### Added
- [common/order-processor] Order Processor - initial release
- [common/order-processor] Amazon Order process implemented
- [common/order-processor] publisher script added
### Changed
- [amazon/pull-orders] Override feature of ERP setting
### Fixed
- [amazon/pull-orders] Exception handling of ASM is improved
- [common/order-processor] Exception handling of ASM is improved


## [0.0.3] - 2023-08-24

### Added
- [common/order-pre-processor] Order Pre Processor - initial release

## [0.0.2] - 2023-08-24

### Changed
- [amazon/pull-orders] Only new order is published to SNS channel
### Fixed
- [amazon/pull-orders] Empty BuyerInfo causing JSON parsing error 
## [0.0.1] - 2023-08-16
- [amazon] Amazon Order Pull - initial release