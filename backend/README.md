# Backend API - Hiya Cars Rental

FastAPI backend for the Hiya Cars car rental platform with Supabase integration.

## Prerequisites

- Python 3.10 or 3.11
- Supabase account (for database, auth, and storage)
- Stripe account (for payments)
- RTA API credentials (for contract submission - optional)

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key

# JWT
SECRET_KEY=generate-a-secure-random-key-at-least-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# OAuth (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# RTA (Optional)
RTA_API_URL=https://api.rta.ae/sandbox
RTA_API_KEY=your_rta_api_key
RTA_ENVIRONMENT=sandbox

# App Settings
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:8081

# Platform Fee
PLATFORM_FEE_PERCENTAGE=10.0
```

### 3. Set Up Supabase Database

1. Go to your Supabase project SQL editor
2. Run the SQL schema from `database/schema.sql`
3. This will create all necessary tables and indexes

### 4. Set Up Supabase Storage

Follow the guide in `SUPABASE_STORAGE_SETUP.md` to:
1. Create storage buckets (`avatars`, `kyc-documents`, `vehicle-images`, `contracts`)
2. Configure RLS policies
3. Test file uploads

**Note:** The app now uses **Supabase Storage** instead of AWS S3 for all file uploads.

### 5. Start the API Server

```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
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
│   │       ├── auth.py          # Authentication + avatar upload
│   │       ├── vehicles.py      # Vehicle management + image upload
│   │       ├── bookings.py      # Booking management
│   │       ├── payments.py      # Payment processing
│   │       ├── kyc.py           # KYC verification + document upload
│   │       ├── contracts.py     # Contract management
│   │       ├── loyalty.py       # Loyalty points
│   │       └── reviews.py       # Reviews and ratings
│   ├── models/                  # Pydantic models
│   ├── auth.py                  # Authentication utilities
│   ├── database.py              # Database connection
│   └── storage.py               # Supabase Storage service
├── config.py                    # Configuration settings
├── main.py                      # FastAPI application
├── requirements.txt             # Python dependencies
├── Procfile                     # Railway deployment config
└── runtime.txt                  # Python version for Railway
```

## Key Features

### Authentication
- ✅ Email/Password registration and login (Supabase Auth)
- ✅ JWT token-based authentication
- ✅ Profile picture upload
- 🔄 Google OAuth (configured, needs frontend)
- 🔄 Facebook OAuth (configured, needs frontend)
- ⏳ Phone OTP (placeholder)

### File Storage (NEW - Supabase Storage)
- ✅ User avatar/profile pictures
- ✅ KYC document uploads (ID, passport, license, visa)
- ✅ Digital signature capture
- ✅ Vehicle image uploads
- ✅ Contract PDFs (ready)

### Vehicle Management
- ✅ CRUD operations for vehicles
- ✅ Advanced search with filters
- ✅ Availability checking
- ✅ Multi-tenant support
- ✅ Vehicle image management

### Booking System
- ✅ 3-step booking flow
- ✅ Surge pricing calculation
- ✅ Driver option
- ✅ Price calculation based on rental type

### Payments
- ✅ Stripe integration
- ✅ Payment intent creation
- ✅ Webhook handling
- ✅ Wallet and loyalty points support

### KYC
- ✅ Document upload to Supabase Storage
- ✅ Signature capture
- ✅ Status tracking
- ✅ Admin review workflow

### Loyalty & Reviews
- ✅ Points earning and redemption
- ✅ Rating and review system

## Deployment

### Railway Deployment

This backend is configured for Railway deployment:

1. **Push to GitHub**:
   ```bash
   git push origin main
   ```

2. **Connect to Railway**:
   - Go to railway.app
   - Create new project from GitHub repo
   - Set root directory to `backend`
   - Add environment variables (see above)

3. **Automatic Deploy**:
   - Railway will automatically detect Procfile
   - Python 3.10 runtime specified in runtime.txt
   - Builds and deploys on every push

### Required Environment Variables for Railway

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
SECRET_KEY=your-secure-secret-key
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com
```

## Storage Setup

The app uses **Supabase Storage** for all file uploads. Follow these steps:

1. Create buckets in Supabase Dashboard:
   - `avatars` (public)
   - `kyc-documents` (private)
   - `vehicle-images` (public)
   - `contracts` (private)

2. Configure RLS policies (see `SUPABASE_STORAGE_SETUP.md`)

3. Test uploads from API documentation

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update profile
- `POST /api/v1/auth/me/avatar` - Upload avatar **[NEW]**
- `POST /api/v1/auth/refresh` - Refresh token

### Vehicles
- `GET /api/v1/vehicles/` - List vehicles
- `GET /api/v1/vehicles/search` - Search vehicles
- `GET /api/v1/vehicles/{id}` - Get vehicle details
- `POST /api/v1/vehicles/` - Create vehicle (Admin)
- `PUT /api/v1/vehicles/{id}` - Update vehicle (Admin)
- `DELETE /api/v1/vehicles/{id}` - Delete vehicle (Admin)
- `GET /api/v1/vehicles/{id}/availability` - Check availability
- `POST /api/v1/vehicles/{id}/images` - Upload vehicle image **[NEW]**
- `DELETE /api/v1/vehicles/{id}/images` - Delete vehicle image **[NEW]**

### KYC
- `POST /api/v1/kyc/` - Create KYC application
- `GET /api/v1/kyc/` - Get user KYC
- `POST /api/v1/kyc/documents/{type}?side=front` - Upload document **[UPDATED]**
- `POST /api/v1/kyc/signature` - Upload signature **[UPDATED]**
- `PUT /api/v1/kyc/{id}` - Update KYC status (Admin)

### Bookings, Payments, Contracts, Loyalty, Reviews
See Swagger UI for complete endpoint documentation.

## Notes

- All timestamps are in UTC
- All monetary values are in AED (UAE Dirhams)
- JWT tokens expire after 30 minutes (configurable)
- Platform fee is 10% (configurable)
- File uploads handled by Supabase Storage (no AWS needed)
- Max file sizes: 2MB (avatars), 5MB (vehicle images), 10MB (documents)



