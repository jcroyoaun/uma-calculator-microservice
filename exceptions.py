class VoucherError(Exception):
    """Base exception for voucher related errors"""
    def __init__(self, message, code=400):
        self.message = message
        self.code = code
        super().__init__(self.message)

class LimitExceededError(VoucherError):
    """Raised when voucher amount exceeds limits"""
    pass

class InvalidAmountError(VoucherError):
    """Raised when amount is invalid"""
    pass
