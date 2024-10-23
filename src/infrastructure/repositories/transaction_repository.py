from datetime import datetime
from decimal import Decimal

from src.domain.models import VoucherTransaction
from src.infrastructure.database import db

class TransactionModel(db.Model):
    """Database model for voucher transactions"""
    __tablename__ = 'voucher_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TransactionRepository:
    def get_annual_total(self, year: int) -> Decimal:
        """Get total vouchers issued for a specific year"""
        total = db.session.query(
            db.func.sum(TransactionModel.amount)
        ).filter(
            db.extract('year', TransactionModel.transaction_date) == year
        ).scalar()
        return total or Decimal('0')

    def save(self, transaction: VoucherTransaction) -> None:
        """Save new transaction"""
        record = TransactionModel(
            amount=transaction.amount,
            transaction_date=transaction.transaction_date
        )
        db.session.add(record)
        db.session.commit()
