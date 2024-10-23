import logging
import requests
from datetime import datetime
from typing import Optional, Tuple
import os

from src.domain.models import UMAValue
from src.infrastructure.repositories.uma_repository import UMARepository

logger = logging.getLogger(__name__)

class INEGIService:
    BASE_URL = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml"
    UMA_INDICATOR = "628194"

    def __init__(self, uma_repository: UMARepository):
        self.api_key = os.environ.get('INEGI_API_KEY')
        if not self.api_key:
            raise ValueError("INEGI API key not found in environment variables")
        
        self.uma_repository = uma_repository
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0'
        })

    def _format_date(self, date_str: str) -> datetime:
        """Convert date format to datetime"""
        try:
            if len(date_str.split('/')) == 2:
                year, month = date_str.split('/')
                return datetime(int(year), int(month), 1)
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
            raise

    def _get_latest_value(self) -> Optional[Tuple[float, datetime]]:
        """Fetch the latest UMA value from INEGI's API"""
        try:
            params = {'type': 'json'}
            url = f"{self.BASE_URL}/INDICATOR/{self.UMA_INDICATOR}/es/0/false/BIE/2.0/{self.api_key}"
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            series = data.get('Series', [{}])[0]
            
            if not series:
                logger.error("No series data found in API response")
                return None
            
            observations = series.get('OBSERVATIONS', [])
            if not observations:
                logger.error("No observations found in series data")
                return None
            
            latest = sorted(observations, key=lambda x: x.get('TIME_PERIOD', ''), reverse=True)[0]
            
            value = float(latest.get('OBS_VALUE', 0))
            date_str = latest.get('TIME_PERIOD', '')
            
            if not value or not date_str:
                logger.error("Invalid value or date in latest observation")
                return None
            
            valid_from = self._format_date(date_str)
            return value, valid_from
            
        except Exception as e:
            logger.error(f"Error fetching UMA value: {str(e)}")
            return None

    def update_uma_value(self) -> Optional[UMAValue]:
        """Update UMA value in the repository"""
        result = self._get_latest_value()
        if not result:
            return None
            
        value, valid_from = result
        uma_value = UMAValue(daily_value=value, valid_from=valid_from)
        
        try:
            self.uma_repository.save(uma_value)
            logger.info(f"Updated UMA value to {value} valid from {valid_from}")
            return uma_value
            
        except Exception as e:
            logger.error(f"Error saving UMA value: {str(e)}")
            return None
