"""Constants and configuration values for datacrafter."""
DATETIME_PATTERNS = [
    '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M:%S%z', '%d.%m.%Y', '%d.%m.%Y %H:%M:%S',
    '%Y-%m-%d', '%Y%m%d'
]

DATE_PATTERNS_SHORT = [
    '%Y-%m-%d', '%d.%m.%Y', '%Y%m%d'
]

DEFAULT_BULK_RECORDS = 250

# Error handling strategies
ERROR_STRATEGY_SKIP = 'skip'  # Skip failed records and continue
ERROR_STRATEGY_FAIL = 'fail'  # Stop processing on first error
ERROR_STRATEGY_RETRY = 'retry'  # Retry failed records

# Retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # seconds
DEFAULT_RETRY_BACKOFF = 2.0  # exponential backoff multiplier
