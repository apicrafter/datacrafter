# Simplified date handling. More advanced used qddate lib
DATE_PATTERNS = ["%d.%m.%Y", "%Y-%m-%d", "%y-%m-%d", "%Y-%m-%dT%H:%M:%S",
                 "%Y-%m-%d %H:%M:%S",
                 "%d.%m.%Y %H:%M"]


DATETIME_PATTERNS = ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S',
                     '%Y-%m-%d %H:%M:%S%z',
                     '%d.%m.%Y', '%d.%m.%Y %H:%M:%S', '%Y-%m-%d',
                     '%Y%m%d']

DATE_PATTERNS_SHORT = ['%Y-%m-%d',
                 '%d.%m.%Y'
                 '%Y%m%d']

DEFAULT_DICT_SHARE = 70

SUPPORTED_FILE_TYPES = ['xls', 'xlsx', 'csv', 'xml', 'json', 'jsonl', 'yaml', 'tsv', 'sql', 'bson', 'parquet']

DEFAULT_OPTIONS = {'encoding': 'utf8',
                   'delimiter': ',',
                   'limit': 1000
                   }

DEFAULT_BULK_RECORDS = 250

# Error handling strategies
ERROR_STRATEGY_SKIP = 'skip'  # Skip failed records and continue
ERROR_STRATEGY_FAIL = 'fail'  # Stop processing on first error
ERROR_STRATEGY_RETRY = 'retry'  # Retry failed records

# Retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # seconds
DEFAULT_RETRY_BACKOFF = 2.0  # exponential backoff multiplier