from marshmallow import Schema, fields

class VoucherAmountSchema(Schema):
    amount = fields.Float(required=True, description="Voucher amount to validate")
    transaction_date = fields.Date(required=False, description="Transaction date (optional)")

class LimitResponseSchema(Schema):
    is_valid = fields.Boolean(description="Whether the amount is within limits")
    current_amount = fields.Float(description="Current voucher amount")
    limit = fields.Float(description="Maximum limit")
    remaining = fields.Float(description="Remaining amount available")
    message = fields.String(description="Error message if any")

class UMAResponseSchema(Schema):
    daily_value = fields.Float(description="Daily UMA value")
    monthly_value = fields.Float(description="Monthly UMA value")
    max_monthly_deposit = fields.Float(description="Maximum monthly deposit allowed")
    max_annual_deposit = fields.Float(description="Maximum annual deposit allowed")
    annual_deposits_allowed = fields.Integer(description="Number of deposits allowed per year")

class RemainingLimitSchema(Schema):
    year = fields.Integer(description="Year for the limit calculation")
    remaining_limit = fields.Float(description="Remaining amount available for the year")
    annual_limit = fields.Float(description="Total annual limit")
