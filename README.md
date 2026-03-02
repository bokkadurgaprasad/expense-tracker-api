# Personal Finance Tracker API

FastAPI backend for managing personal finances with MongoDB.

## Features

- User authentication with JWT tokens
- Password reset functionality
- Bank account management
- Credit card tracking
- EMI management
- Borrow/lend tracking
- Expected cashflow management
- Financial metrics calculation
- Monthly snapshots
- Dashboard with upcoming dues

## Tech Stack

- FastAPI
- MongoDB with PyMongo
- JWT authentication
- Bcrypt password hashing
- Pydantic for validation

## Project Structure

```
expense-tracker-api/
├── db/                      # Database configuration
│   ├── __init__.py
│   └── connection.py        # MongoDB connection management
├── app/
│   ├── config.py           # Application settings
│   ├── models/             # Pydantic models
│   ├── repositories/       # Database operations
│   ├── services/           # Business logic
│   ├── routes/             # API endpoints
│   └── middleware/         # Auth middleware
├── main.py                 # Application entry point
├── seed.py                 # Database seeding script
└── requirements.txt        # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your MongoDB URI and JWT secret
```

### 3. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 4. (Optional) Seed the Database

```bash
python seed.py
```

Test credentials after seeding:
- Username: `john_doe` / Password: `password123`
- Username: `jane_smith` / Password: `password123`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/reset-password` - Reset password (requires authentication)

### Bank Accounts
- `GET /bank-accounts` - List all accounts
- `POST /bank-accounts` - Create account
- `GET /bank-accounts/{id}` - Get account details
- `PUT /bank-accounts/{id}` - Update account
- `DELETE /bank-accounts/{id}` - Delete account

### Credit Cards
- `GET /credit-cards` - List all cards
- `POST /credit-cards` - Create card
- `GET /credit-cards/{id}` - Get card details
- `PUT /credit-cards/{id}` - Update card
- `DELETE /credit-cards/{id}` - Delete card

### EMIs
- `GET /emis` - List all EMIs
- `POST /emis` - Create EMI
- `GET /emis/{id}` - Get EMI details
- `PUT /emis/{id}` - Update EMI
- `DELETE /emis/{id}` - Delete EMI

### Borrows
- `GET /borrows` - List all borrow records
- `POST /borrows` - Create borrow record
- `GET /borrows/{id}` - Get borrow details
- `PUT /borrows/{id}` - Update borrow record
- `DELETE /borrows/{id}` - Delete borrow record

### Cashflows
- `GET /cashflows` - List all cashflows
- `POST /cashflows` - Create cashflow
- `GET /cashflows/{id}` - Get cashflow details
- `PUT /cashflows/{id}` - Update cashflow
- `DELETE /cashflows/{id}` - Delete cashflow

### Dashboard & Metrics
- `GET /dashboard` - Get dashboard data with metrics and upcoming dues
- `GET /financial-engine/metrics` - Get financial metrics
- `GET /snapshots` - List monthly snapshots
- `POST /snapshots` - Create snapshot

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication.

Include JWT token in Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Environment Variables

- `MONGODB_URI` - MongoDB connection string (default: mongodb://localhost:27017)
- `DATABASE_NAME` - Database name (default: personal_finance_tracker)
- `JWT_SECRET_KEY` - Secret key for JWT signing
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_EXPIRATION_DAYS` - Token expiration in days (default: 30)

## Development

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
