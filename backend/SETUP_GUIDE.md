# Setup Guide - Next Steps

## ✅ Step 1: Set Up Database Schema in Supabase

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** (left sidebar)
3. Open the file `database/schema.sql` from this project
4. Copy the entire SQL content (remove the comment at the top)
5. Paste it into the SQL Editor
6. Click **Run** to execute the schema

This will create all necessary tables:
- `users` - User profiles
- `organizations` - Rental agencies/companies
- `vehicles` - Car listings
- `bookings` - Rental bookings
- `payments` - Payment records
- `kyc` - KYC documents
- `contracts` - Rental contracts
- `loyalty_points` - Loyalty system
- `loyalty_transactions` - Points transactions
- `reviews` - Vehicle reviews
- `audit_logs` - Audit trail

## ✅ Step 2: Test the API

### 2.1 Check API Health
Open your browser and visit:
```
http://localhost:8000/health
```

You should see:
```json
{"status": "healthy", "environment": "development"}
```

### 2.2 View API Documentation
Visit the interactive API docs:
```
http://localhost:8000/docs
```

This shows all available endpoints with Swagger UI.

### 2.3 Test User Registration
Using the Swagger UI or a tool like Postman:

**POST** `http://localhost:8000/api/v1/auth/register`
```json
{
  "email": "test@example.com",
  "password": "Test123!",
  "full_name": "Test User",
  "phone": "+971501234567",
  "language": "en"
}
```

### 2.4 Test Login
**POST** `http://localhost:8000/api/v1/auth/login`
- Use form data:
  - `username`: `test@example.com`
  - `password`: `Test123!`

You'll get an `access_token` - save this for authenticated requests.

### 2.5 Test Vehicle Listing
**GET** `http://localhost:8000/api/v1/vehicles/`

## ✅ Step 3: Create Test Data (Optional)

### 3.1 Create an Organization
In Supabase SQL Editor, run:
```sql
INSERT INTO organizations (name, type, email, phone)
VALUES ('Test Rental Agency', 'agency', 'agency@test.com', '+971501234567')
RETURNING id;
```

Save the returned `id` - you'll need it for vehicles.

### 3.2 Create Test Vehicles
```sql
INSERT INTO vehicles (
    make, model, year, category, seats, transmission, fuel_type, color,
    license_plate, price_per_day, price_per_week, price_per_month,
    location, organization_id, images, features
) VALUES (
    'Tesla', 'Model S', 2023, 'electric', 5, 'automatic', 'electric', 'White',
    'ABC-1234', 200.00, 1200.00, 5000.00,
    'Dubai, UAE', 'YOUR_ORGANIZATION_ID_HERE',
    ARRAY['https://example.com/car1.jpg'],
    ARRAY['GPS', 'Bluetooth', 'Sunroof']
);
```

## ✅ Step 4: Connect Mobile App to Backend

### 4.1 Update Mobile App API Base URL

In your React Native app, you'll need to set the API base URL. Create or update a config file:

**File: `mobile/constant/api.js`** (or similar)
```javascript
export const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000'  // Development
  : 'https://your-production-api.com';  // Production

export const API_ENDPOINTS = {
  AUTH: {
    REGISTER: `${API_BASE_URL}/api/v1/auth/register`,
    LOGIN: `${API_BASE_URL}/api/v1/auth/login`,
    ME: `${API_BASE_URL}/api/v1/auth/me`,
  },
  VEHICLES: {
    LIST: `${API_BASE_URL}/api/v1/vehicles/`,
    SEARCH: `${API_BASE_URL}/api/v1/vehicles/search`,
    DETAILS: (id) => `${API_BASE_URL}/api/v1/vehicles/${id}`,
  },
  BOOKINGS: {
    CREATE: `${API_BASE_URL}/api/v1/bookings/`,
    LIST: `${API_BASE_URL}/api/v1/bookings/`,
    DETAILS: (id) => `${API_BASE_URL}/api/v1/bookings/${id}`,
  },
  // ... add more endpoints as needed
};
```

### 4.2 Handle CORS for Mobile App

If testing on a physical device or emulator:
- For Android emulator: Use `http://10.0.2.2:8000` instead of `localhost`
- For iOS simulator: `http://localhost:8000` works
- For physical device: Use your computer's local IP (e.g., `http://192.168.1.100:8000`)

Update `CORS_ORIGINS` in `.env` if needed:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8081,http://10.0.2.2:8000
```

### 4.3 Create API Service in Mobile App

**File: `mobile/services/api.js`** (create this)
```javascript
import { API_BASE_URL } from '../constant/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Auth methods
  async register(userData) {
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    return this.request('/api/v1/auth/login', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async getVehicles(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/v1/vehicles/?${queryString}`);
  }

  // Add more methods as needed
}

export default new ApiService();
```

## ✅ Step 5: Test Integration

### 5.1 Test Registration from Mobile App
```javascript
import ApiService from './services/api';

// In your SignUpScreen
const handleSignUp = async () => {
  try {
    const response = await ApiService.register({
      email: 'user@example.com',
      password: 'Password123!',
      full_name: 'John Doe',
      phone: '+971501234567',
      language: 'en',
    });
    console.log('Registration successful:', response);
  } catch (error) {
    console.error('Registration failed:', error);
  }
};
```

### 5.2 Test Login and Get Vehicles
```javascript
// Login
const loginResponse = await ApiService.login('user@example.com', 'Password123!');
ApiService.setToken(loginResponse.access_token);

// Get vehicles
const vehicles = await ApiService.getVehicles();
console.log('Vehicles:', vehicles);
```

## ✅ Step 6: Next Development Tasks

1. **Complete OAuth Implementations**
   - Google OAuth token verification
   - Facebook OAuth token verification
   - Phone OTP with SMS service (Twilio/AWS SNS)

2. **Set Up File Storage**
   - Configure AWS S3 bucket
   - Test file uploads for KYC documents
   - Test image uploads for vehicles

3. **Set Up Payments**
   - Create Stripe test account
   - Configure Stripe webhook endpoint
   - Test payment flow

4. **Set Up RTA Integration**
   - Get RTA API credentials
   - Implement contract submission
   - Set up status polling

5. **Add Background Jobs**
   - Install and start Redis
   - Start Celery worker
   - Start Celery beat for periodic tasks

## 🔍 Troubleshooting

### API not accessible from mobile app
- Check if backend is running on `0.0.0.0:8000` (not just `127.0.0.1`)
- Verify CORS settings in `.env`
- Check firewall settings

### Database errors
- Ensure schema.sql was run successfully
- Check Supabase connection in `.env`
- Verify table names match (case-sensitive)

### Authentication errors
- Check JWT token expiration
- Verify `SECRET_KEY` is set in `.env`
- Ensure user exists in Supabase `auth.users` table

## 📚 Useful Commands

```bash
# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Check API health
curl http://localhost:8000/health

# View API docs
# Open http://localhost:8000/docs in browser
```

## 🎯 Quick Test Checklist

- [ ] Database schema created in Supabase
- [ ] Backend server running
- [ ] Health endpoint returns 200
- [ ] API docs accessible at /docs
- [ ] User registration works
- [ ] User login works
- [ ] Can list vehicles
- [ ] Mobile app can connect to backend
- [ ] Authentication token works


