# Current UMA values for 2023
DAILY_UMA = 108.57  # Mexican pesos
MONTHLY_UMA = DAILY_UMA * 30.4  # ~3300.53 MXN
ANNUAL_MAX_DEPOSITS = 7  # Maximum number of UMA deposits per year
MAX_MONTHLY_AMOUNT = MONTHLY_UMA  # Maximum monthly deposit amount
MAX_ANNUAL_AMOUNT = MONTHLY_UMA * ANNUAL_MAX_DEPOSITS  # ~23,103.71 MXN

# Error messages
ERRORS = {
    'EXCEED_MONTHLY': 'Amount exceeds monthly UMA limit of {:.2f} MXN',
    'EXCEED_ANNUAL': 'Amount would exceed annual UMA limit of {:.2f} MXN',
    'INVALID_AMOUNT': 'Amount must be a positive number',
}
