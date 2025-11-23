# Mobile App Setup Guide

## ✅ Step 1: Install Dependencies

Run the following command in the `mobile` directory:

```bash
cd mobile
npm install
```

This will install all dependencies including the new `@react-native-async-storage/async-storage` package.

## ✅ Step 2: Configure API Base URL

The API base URL is automatically configured in `constant/api.js` based on your platform:

- **Android Emulator**: `http://10.0.2.2:8000`
- **iOS Simulator**: `http://localhost:8000`
- **Physical Device**: You'll need to use your computer's local IP address (e.g., `http://192.168.1.100:8000`)

### For Physical Device Testing:

1. Find your computer's local IP address:
   - **Windows**: Run `ipconfig` in Command Prompt and look for IPv4 Address
   - **Mac/Linux**: Run `ifconfig` and look for inet address

2. Update `constant/api.js` if needed, or set it in your `.env` file:

```javascript
// In constant/api.js, you can modify getApiBaseUrl() function
const getApiBaseUrl = () => {
  if (__DEV__) {
    // For physical device, replace with your computer's IP
    return 'http://192.168.1.XXX:8000'; // Replace XXX with your IP
  }
  // ...
};
```

3. Make sure your backend is running with `--host 0.0.0.0`:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Make sure your computer and mobile device are on the same WiFi network.

## ✅ Step 3: Update Backend CORS Settings

In your backend `.env` file, make sure CORS_ORIGINS includes your mobile app origins:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8081,http://10.0.2.2:8000
```

Or you can update `config.py` to allow all origins in development:

```python
CORS_ORIGINS: str = "*"  # Only for development
```

## ✅ Step 4: Test the Connection

1. **Start the backend server**:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the mobile app**:
   ```bash
   cd mobile
   npm start
   # Then press 'a' for Android or 'i' for iOS
   ```

3. **Test Registration**:
   - Open the app
   - Navigate to Sign Up
   - Fill in the form and submit
   - You should see a success message

4. **Test Login**:
   - Use the credentials you just created
   - You should be logged in and redirected to the home screen

5. **Test Vehicle Listing**:
   - The home screen should load vehicles from the backend
   - If no vehicles are shown, make sure you've created some test vehicles in Supabase

## ✅ Step 5: Create Test Data

If you haven't already, create some test vehicles in your Supabase database:

1. Go to Supabase SQL Editor
2. Run this SQL to create a test organization and vehicle:

```sql
-- Create organization
INSERT INTO organizations (name, type, email, phone)
VALUES ('Test Rental Agency', 'agency', 'agency@test.com', '+971501234567')
RETURNING id;

-- Note the organization_id from above, then create a vehicle
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

## 🔍 Troubleshooting

### App can't connect to backend

1. **Check backend is running**: Visit `http://localhost:8000/health` in your browser
2. **Check API URL**: Verify the URL in `constant/api.js` matches your setup
3. **Check CORS**: Make sure CORS is configured correctly in backend
4. **Check network**: For physical devices, ensure same WiFi network
5. **Check firewall**: Make sure firewall allows connections on port 8000

### Authentication not working

1. **Check token storage**: Verify AsyncStorage is working
2. **Check API response**: Look at network requests in React Native Debugger
3. **Check backend logs**: Look for errors in backend console

### Vehicles not loading

1. **Check database**: Verify vehicles exist in Supabase
2. **Check API response**: Test the vehicles endpoint in Swagger UI
3. **Check network requests**: Use React Native Debugger to see API calls
4. **Check error logs**: Look for errors in app console

## 📱 Next Steps

1. **Complete Booking Flow**: Update BookingDetailsScreen to use API
2. **Add Payment Integration**: Integrate Stripe in PaymentMethodsScreen
3. **Add KYC Flow**: Implement document upload for KYC
4. **Add Profile Management**: Update AccountScreen to show user data
5. **Add Search Functionality**: Implement vehicle search with filters

## 🎯 Testing Checklist

- [ ] App connects to backend
- [ ] User registration works
- [ ] User login works
- [ ] Token is stored correctly
- [ ] Vehicles are fetched and displayed
- [ ] Pull-to-refresh works
- [ ] Error handling works (network errors, etc.)


