# UMA Calculator Microservice

A focused API microservice for calculating food voucher limits under ISR rules using current UMA values.

## Features

- Automated UMA value updates from INEGI's official API
- Food voucher limit validation according to ISR rules
- Remaining limit calculations
- Swagger UI documentation for all endpoints

## API Endpoints

- `/api/v1/uma` - Get current UMA values
- `/api/v1/vouchers/validate` - Validate voucher amounts
- `/api/v1/vouchers/remaining` - Check remaining limits

## Requirements

- Python 3.11+
- PostgreSQL database
- INEGI API key for UMA updates

## Setup

1. Set required environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `INEGI_API_KEY`: API key for INEGI's service

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   flask db upgrade
   ```

4. Start the server:
   ```bash
   python main.py
   ```

## Documentation

API documentation is available at `/swagger-ui/` when the server is running.

## Commands

- `flask update-uma`: Update UMA values from INEGI's API

## License

MIT
