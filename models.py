from datetime import datetime
from database import db

class UMAValue(db.Model):
    """Stores historical UMA values"""
    id = db.Column(db.Integer, primary_key=True)
    daily_value = db.Column(db.Numeric(10, 2), nullable=False)
    valid_from = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VoucherTransaction(db.Model):
    """Tracks food voucher deposits"""
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def get_annual_total(cls, year):
        """Get total vouchers issued for a specific year"""
        return db.session.query(
            db.func.sum(cls.amount)
        ).filter(
            db.extract('year', cls.transaction_date) == year
        ).scalar() or 0
