from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.domain.models import UMAValue
from src.infrastructure.database import db

class UMAValueModel(db.Model):
    """Database model for UMA values"""
    __tablename__ = 'uma_values'
    
    id = db.Column(db.Integer, primary_key=True)
    daily_value = db.Column(db.Numeric(10, 2), nullable=False)
    valid_from = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UMARepository:
    def get_current_value(self) -> Optional[UMAValue]:
        """Get current UMA value"""
        record = UMAValueModel.query.order_by(
            UMAValueModel.valid_from.desc()
        ).first()
        
        if record:
            return UMAValue(
                daily_value=record.daily_value,
                valid_from=record.valid_from
            )
        return None

    def save(self, uma_value: UMAValue) -> None:
        """Save new UMA value"""
        record = UMAValueModel(
            daily_value=uma_value.daily_value,
            valid_from=uma_value.valid_from
        )
        db.session.add(record)
        db.session.commit()
