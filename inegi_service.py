import logging
import requests
from datetime import datetime
from typing import Optional, Tuple
import os

from app import db
from models import UMAValue

logger = logging.getLogger(__name__)

class INEGIService:
    # INEGI API endpoints
    BASE_URL = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml"
    # UMA indicator ID in INEGI's system
    UMA_INDICATOR = "628194"  # This is the indicator ID for UMA
    
    def __init__(self):
        self.api_key = os.environ.get('INEGI_API_KEY')
        if not self.api_key:
            raise ValueError("INEGI API key not found in environment variables")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _format_date(self, date_str: str) -> datetime:
        """Convert date format to datetime"""
        try:
            # Try YYYY/MM format first (what we're receiving from API)
            if len(date_str.split('/')) == 2:
                year, month = date_str.split('/')
                # Set the day to 1 since we only get year and month
                return datetime(int(year), int(month), 1)
            # Fallback to YYYY-MM-DD format
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
            raise
    
    def _get_latest_value(self) -> Optional[Tuple[float, datetime]]:
        """
        Fetch the latest UMA value from INEGI's API
        Returns tuple of (value, valid_from_date) or None if fetch fails
        """
        try:
            # Construct API URL with parameters according to INEGI's documentation
            params = {
                'type': 'json'
            }
            url = f"{self.BASE_URL}/INDICATOR/{self.UMA_INDICATOR}/es/0/false/BIE/2.0/{self.api_key}"
            
            # Make API request
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Extract the Series data which contains the UMA values
            series = data.get('Series', [{}])[0]
            if not series:
                logger.error("No series data found in API response")
                return None
            
            # Get the latest observation
            observations = series.get('OBSERVATIONS', [])
            if not observations:
                logger.error("No observations found in series data")
                return None
            
            # Sort observations by date to get the latest
            latest = sorted(observations, key=lambda x: x.get('TIME_PERIOD', ''), reverse=True)[0]
            
            # Extract value and date
            value = float(latest.get('OBS_VALUE', 0))
            date_str = latest.get('TIME_PERIOD', '')
            
            if not value or not date_str:
                logger.error("Invalid value or date in latest observation")
                return None
            
            # Parse date - API returns dates in YYYY/MM format
            valid_from = self._format_date(date_str)
            
            return value, valid_from
                
        except requests.RequestException as e:
            logger.error(f"Error fetching UMA value from API: {str(e)}")
            return None
        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Error parsing API response: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while fetching UMA value: {str(e)}")
            return None
    
    def update_uma_value(self) -> Optional[UMAValue]:
        """
        Fetch and store the latest UMA value
        Returns the new UMAValue object if successful, None otherwise
        """
        result = self._get_latest_value()
        if not result:
            return None
            
        value, valid_from = result
        
        try:
            # Check if we already have this value
            existing = UMAValue.query.filter_by(
                daily_value=value,
                valid_from=valid_from.date()
            ).first()
            
            if existing:
                logger.info("UMA value already up to date")
                return existing
                
            # Create new UMA value record
            new_value = UMAValue(
                daily_value=value,
                valid_from=valid_from.date()
            )
            
            db.session.add(new_value)
            db.session.commit()
            logger.info(f"Updated UMA value to {value} valid from {valid_from}")
            return new_value
            
        except Exception as e:
            logger.error(f"Error saving UMA value: {str(e)}")
            db.session.rollback()
            return None
