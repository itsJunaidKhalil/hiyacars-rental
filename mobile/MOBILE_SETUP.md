# Mobile App Setup Guide

## Prerequisites

- Node.js 18.x or higher
- npm or yarn
- Expo CLI: `npm install -g @expo/cli`
- Expo Go app (for testing on physical devices)

## ✅ Step 1: Install Dependencies

Run the following command in the `mobile` directory:

```bash
cd mobile
npm install
```

This will install all dependencies including:
- React Native & Expo
- Supabase JS client
- AsyncStorage for token persistence
- Expo ImagePicker & DocumentPicker for file uploads

## ✅ Step 2: Configure Environment Variables

Create a `.env` file in the `mobile` directory:

```env
# Supabase Configuration
EXPO_PUBLIC_SUPABASE_URL=https://wcxmmdujcujrvhwmqyjq.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here

# API Configuration (for development)
EXPO_PUBLIC_API_URL=http://localhost:8000

# For production (after deploying backend to Railway)
# EXPO_PUBLIC_API_URL=https://your-app.railway.app
```

**Note**: Make sure to update these values with your actual Supabase credentials.

## ✅ Step 3: Configure API Base URL

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
  return process.env.EXPO_PUBLIC_API_URL || 'https://your-production-api.railway.app';
};
```

3. Make sure your backend is running with `--host 0.0.0.0`:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Ensure your computer and mobile device are on the same WiFi network.

## ✅ Step 4: File Upload Features

The app now includes **Supabase Storage** integration for file uploads:

### Available Storage Functions:

Located in `services/storage.js`:

```javascript
import {
  uploadAvatar,           // Upload profile picture
  uploadKYCDocument,      // Upload ID/passport/license
  uploadVehicleImage,     // Upload car photos
  pickImageFromCamera,    // Take photo with camera
  pickImageFromGallery,   // Select from gallery
  pickDocument,           // Select PDF/document
} from './services/storage';
```

### Example Usage:

```javascript
// Upload profile picture
const image = await pickImageFromGallery();
const avatarUrl = await uploadAvatar(userId, image);

// Upload KYC document
const kycImage = await pickImageFromCamera();
const kycUrl = await uploadKYCDocument(userId, 'emirates_id', 'front', kycImage);

// Upload vehicle image
const vehicleImage = await pickImageFromGallery();
const vehicleUrl = await uploadVehicleImage(vehicleId, vehicleImage);
```

### Required Supabase Buckets:

Make sure these buckets are created in Supabase Dashboard:
- `avatars` (for profile pictures)
- `kyc-documents` (for ID verification)
- `vehicle-images` (for car photos)
- `contracts` (for rental agreements)

See `SUPABASE_STORAGE_SETUP.md` in the root directory for setup instructions.

## ✅ Step 5: Update Backend CORS Settings (Optional)

In your backend `.env` file, make sure CORS_ORIGINS includes your mobile app origins:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8081,http://10.0.2.2:8000
```

Or you can update `config.py` to allow all origins in development:

```python
CORS_ORIGINS: str = "*"  # Only for development
```

## ✅ Step 6: Test the Connection

1. **Start the backend server** (or use Railway URL):
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

3. **Test Features**:
   - ✅ User registration
   - ✅ User login
   - ✅ Profile picture upload
   - ✅ Vehicle listing
   - ✅ KYC document upload
   - ✅ Booking flow

## ✅ Step 7: Building APK/AAB

### Development Build:

```bash
eas build --profile preview --platform android
```

### Production Build:

```bash
eas build --profile production --platform android
```

**Note**: Make sure environment variables are configured in EAS:

```bash
eas secret:create --scope project --name EXPO_PUBLIC_SUPABASE_URL --value "https://your-project.supabase.co"
eas secret:create --scope project --name EXPO_PUBLIC_SUPABASE_ANON_KEY --value "your_key"
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-app.railway.app"
```

## ✅ Step 8: Create Test Data

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

1. **Check Supabase credentials**: Verify `.env` has correct Supabase URL and key
2. **Check token storage**: Verify AsyncStorage is working
3. **Check API response**: Look at network requests in React Native Debugger
4. **Check backend logs**: Look for errors in backend console

### File upload not working

1. **Check Supabase buckets**: Verify buckets are created in Supabase Dashboard
2. **Check RLS policies**: Ensure proper access policies are configured
3. **Check permissions**: Camera/gallery permissions must be granted
4. **Check file size**: Max 2MB for avatars, 5MB for vehicle images, 10MB for documents

### Vehicles not loading

1. **Check database**: Verify vehicles exist in Supabase
2. **Check API response**: Test the vehicles endpoint in Swagger UI
3. **Check network requests**: Use React Native Debugger to see API calls
4. **Check error logs**: Look for errors in app console

## 📱 Features Implemented

- ✅ User authentication (Supabase Auth)
- ✅ Profile management with avatar upload
- ✅ Vehicle browsing and search
- ✅ KYC verification with document upload
- ✅ Booking flow
- ✅ Payment integration (Stripe)
- ✅ File uploads (Supabase Storage)
- ✅ Offline token persistence (AsyncStorage)
- ✅ Deep linking for OAuth callbacks

## 🎯 Testing Checklist

- [ ] App connects to backend
- [ ] User registration works
- [ ] User login works
- [ ] Token is stored correctly
- [ ] Profile picture upload works
- [ ] Vehicles are fetched and displayed
- [ ] KYC document upload works
- [ ] Pull-to-refresh works
- [ ] Error handling works (network errors, etc.)
- [ ] Camera/gallery picker works
- [ ] File uploads to Supabase Storage work

## 📚 Next Steps

1. **Deploy Backend**: Deploy to Railway for production URL
2. **Update API URL**: Point mobile app to Railway URL
3. **Test File Uploads**: Verify all upload features work in production
4. **Submit to Stores**: Build production APK/IPA and submit to app stores

## 🔗 Useful Links

- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)
- [Expo ImagePicker Docs](https://docs.expo.dev/versions/latest/sdk/imagepicker/)
- [EAS Build Docs](https://docs.expo.dev/build/introduction/)
- [Railway Deployment Guide](https://docs.railway.app/)


