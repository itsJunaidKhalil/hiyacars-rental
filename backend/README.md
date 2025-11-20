# README for Backend Setup

## Prerequisites

- Python 3.9+
- PostgreSQL (via Supabase)
- Redis (for Celery background jobs)
- AWS S3 account (for file storage)
- Stripe account (for payments)
- RTA API credentials (for contract submission)

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Update the following:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key
- `SECRET_KEY`: Generate a secure random key for JWT
- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_BUCKET_NAME`: S3 bucket name
- `RTA_API_KEY`: RTA API key

### 3. Set Up Supabase Database

1. Go to your Supabase project SQL editor
2. Run the SQL schema from `database/schema.sql`
3. This will create all necessary tables and indexes

### 4. Run Database Migrations

The schema.sql file contains all table definitions. Run it in Supabase SQL editor.

### 5. Start Redis (for background jobs)

```bash
# On Windows (using WSL or Docker)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

### 6. Start the API Server

```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Start Celery Worker (for background jobs)

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

### 8. Start Celery Beat (for periodic tasks)

```bash
celery -A app.workers.celery_app beat --loglevel=info
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── vehicles.py       # Vehicle management
│   │       ├── bookings.py       # Booking management
│   │       ├── payments.py       # Payment processing
│   │       ├── kyc.py            # KYC verification
│   │       ├── contracts.py     # Contract management
│   │       ├── loyalty.py        # Loyalty points
│   │       └── reviews.py       # Reviews and ratings
│   ├── models/                   # Pydantic models
│   ├── workers/                  # Celery background jobs
│   ├── auth.py                   # Authentication utilities
│   └── database.py               # Database connection
├── config.py                     # Configuration settings
├── main.py                       # FastAPI application
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment variables template
```

## Key Features Implemented

### Authentication
- Email/Password registration and login
- Google OAuth (placeholder - needs implementation)
- Facebook OAuth (placeholder - needs implementation)
- Phone OTP (placeholder - needs implementation)
- JWT token-based authentication

### Vehicle Management
- CRUD operations for vehicles
- Advanced search with filters
- Availability checking
- Multi-tenant support

### Booking System
- 3-step booking flow
- Surge pricing calculation
- Driver option
- Price calculation based on rental type

### Payments
- Stripe integration
- Payment intent creation
- Webhook handling
- Wallet and loyalty points support (partial)

### KYC
- Document upload (Emirates ID, Passport, Driving License)
- Signature capture
- Status tracking
- Admin review workflow

### Contracts
- PDF generation (placeholder)
- RTA integration structure
- Signature workflow
- Status tracking

### Loyalty Points
- Points earning from bookings
- Points redemption
- Expiration handling
- Transaction history

### Reviews
- Rating and review submission
- Vehicle rating aggregation
- Review management

## Next Steps

1. **Complete OAuth Implementations**
   - Implement Google OAuth token verification
   - Implement Facebook OAuth token verification
   - Integrate SMS service for phone OTP

2. **Complete RTA Integration**
   - Implement actual RTA API calls
   - Handle RTA responses
   - Set up webhook endpoints for RTA callbacks

3. **File Upload**
   - Complete S3 integration
   - Add image optimization
   - Implement signature capture endpoint

4. **PDF Generation**
   - Implement contract PDF generation using ReportLab
   - Add contract templates
   - Include Arabic language support

5. **Background Jobs**
   - Complete fines and Salik sync
   - Implement payout processing
   - Add email notifications

6. **Multi-language Support**
   - Add translation middleware
   - Implement Arabic translations
   - RTL support for Arabic

7. **Testing**
   - Add unit tests
   - Add integration tests
   - Set up test database

8. **Deployment**
   - Set up production environment
   - Configure CI/CD
   - Set up monitoring and logging

## Environment Variables Reference

See `.env.example` for all required environment variables.

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/google` - Google OAuth
- `POST /api/v1/auth/facebook` - Facebook OAuth
- `POST /api/v1/auth/phone/otp/send` - Send OTP
- `POST /api/v1/auth/phone/otp/verify` - Verify OTP
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update profile

### Vehicles
- `GET /api/v1/vehicles/` - List vehicles
- `GET /api/v1/vehicles/search` - Search vehicles
- `GET /api/v1/vehicles/{id}` - Get vehicle details
- `POST /api/v1/vehicles/` - Create vehicle (Admin)
- `PUT /api/v1/vehicles/{id}` - Update vehicle (Admin)
- `DELETE /api/v1/vehicles/{id}` - Delete vehicle (Admin)
- `GET /api/v1/vehicles/{id}/availability` - Check availability

### Bookings
- `POST /api/v1/bookings/` - Create booking
- `GET /api/v1/bookings/` - List user bookings
- `GET /api/v1/bookings/{id}` - Get booking details
- `PUT /api/v1/bookings/{id}` - Update booking
- `POST /api/v1/bookings/{id}/cancel` - Cancel booking

### Payments
- `POST /api/v1/payments/intent` - Create payment intent
- `POST /api/v1/payments/webhook` - Stripe webhook
- `GET /api/v1/payments/{id}` - Get payment details

### KYC
- `POST /api/v1/kyc/` - Create KYC application
- `GET /api/v1/kyc/` - Get user KYC
- `POST /api/v1/kyc/documents/{type}` - Upload document
- `POST /api/v1/kyc/signature` - Upload signature
- `PUT /api/v1/kyc/{id}` - Update KYC status (Admin)

### Contracts
- `POST /api/v1/contracts/` - Create contract
- `GET /api/v1/contracts/{id}` - Get contract
- `POST /api/v1/contracts/{id}/sign` - Sign contract
- `POST /api/v1/contracts/{id}/submit-rta` - Submit to RTA

### Loyalty
- `GET /api/v1/loyalty/points` - Get loyalty points
- `GET /api/v1/loyalty/transactions` - Get transactions
- `POST /api/v1/loyalty/earn` - Earn points
- `POST /api/v1/loyalty/redeem` - Redeem points

### Reviews
- `POST /api/v1/reviews/` - Create review
- `GET /api/v1/reviews/vehicle/{id}` - Get vehicle reviews
- `PUT /api/v1/reviews/{id}` - Update review
- `DELETE /api/v1/reviews/{id}` - Delete review

## Notes

- All timestamps are in UTC
- All monetary values are in AED (UAE Dirhams)
- JWT tokens expire after 30 minutes (configurable)
- Platform fee is 10% (configurable)
- Loyalty points expire after 1 year



