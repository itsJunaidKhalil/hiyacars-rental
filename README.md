# 🚗 Hiya Cars Rental

A modern, full-stack car rental application with React Native mobile app and FastAPI backend.

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Mobile App Setup](#mobile-app-setup)
- [Backend Setup](#backend-setup)
- [Railway Deployment](#railway-deployment)
- [Environment Variables](#environment-variables)
- [Features](#features)

---

## 🎯 Overview

Hiya Cars is a complete car rental platform featuring:
- 📱 Mobile app for iOS and Android
- 🔐 Supabase authentication
- 💳 Stripe payment integration
- 📄 Digital contract management
- 🎁 Loyalty rewards program
- ⭐ Reviews and ratings

---

## 🛠️ Tech Stack

### Mobile App
- **Framework:** React Native with Expo
- **Language:** JavaScript
- **Navigation:** Expo Router
- **State Management:** React Context
- **Storage:** AsyncStorage
- **Auth:** Supabase

### Backend
- **Framework:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Storage:** Supabase Storage
- **Auth:** Supabase JWT
- **Payments:** Stripe
- **Deployment:** Railway

---

## 📁 Project Structure

```
hiyacars-rental/
├── mobile/              # React Native mobile app
│   ├── app/            # Expo Router pages
│   ├── components/     # Reusable components
│   ├── services/       # API services
│   ├── constant/       # Constants and config
│   └── .env           # Environment variables
├── backend/            # FastAPI backend
│   ├── app/           # Application code
│   │   ├── api/       # API endpoints
│   │   ├── models/    # Data models
│   │   └── auth_supabase.py  # Supabase authentication
│   ├── config.py      # Configuration
│   └── main.py        # Application entry point
├── docs/              # Documentation
└── README.md          # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18.x or higher
- **Python** 3.10 or higher
- **Expo CLI:** `npm install -g @expo/cli eas-cli`
- **Supabase Account:** https://supabase.com
- **Railway Account:** https://railway.app (for deployment)

---

## 📱 Mobile App Setup

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. Configure Environment Variables

Create `mobile/.env`:

```env
# API Configuration
EXPO_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration
EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

**For different environments:**

```env
# Local Backend
EXPO_PUBLIC_API_URL=http://localhost:8000          # iOS Simulator
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000          # Android Emulator
EXPO_PUBLIC_API_URL=http://192.168.1.XXX:8000     # Physical Device

# Production (Railway)
EXPO_PUBLIC_API_URL=https://your-app.railway.app
```

### 3. Run the App

```bash
# Start Expo development server
npx expo start --clear

# Run on Android
npx expo start --android

# Run on iOS (macOS only)
npx expo start --ios

# Run on web
npx expo start --web
```

### 4. Using Expo Go

1. Install **Expo Go** on your device ([Android](https://play.google.com/store/apps/details?id=host.exp.exponent) | [iOS](https://apps.apple.com/app/expo-go/id982107779))
2. Scan the QR code from the terminal
3. App will load on your device

---

## 🔧 Backend Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `backend/.env`:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# JWT
SECRET_KEY=your-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Settings
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=*

# Platform Fee
PLATFORM_FEE_PERCENTAGE=10.0
```

### 3. Run the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

**API Documentation:** http://localhost:8000/docs

---

## 🚂 Railway Deployment

### 1. Prepare Repository

Your repository is already configured with:
- ✅ `backend/Procfile` - Tells Railway how to start the app
- ✅ `backend/runtime.txt` - Python version
- ✅ `backend/requirements.txt` - Dependencies

### 2. Deploy to Railway

1. Go to https://railway.app
2. Create new project → **Deploy from GitHub repo**
3. Select your repository
4. **Configure Root Directory:**
   - Settings → Service → Root Directory → `backend`

### 3. Add Environment Variables

In Railway Dashboard → Variables tab, add:

```env
# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# JWT (Required)
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Settings (Required)
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=*
PLATFORM_FEE_PERCENTAGE=10.0
```

### 4. Get Deployment URL

1. Railway Dashboard → Service → Settings → Domains
2. Click **"Generate Domain"**
3. Copy your URL: `https://your-app.railway.app`

### 5. Connect Mobile App to Railway

Update `mobile/.env`:

```env
EXPO_PUBLIC_API_URL=https://your-app.railway.app
```

Restart Expo:

```bash
npx expo start --clear
```

### 6. Set EAS Secret (For Production Builds)

```bash
cd mobile
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-app.railway.app"
```

---

## 🔐 Environment Variables

### Mobile App (`mobile/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `EXPO_PUBLIC_API_URL` | Backend API URL | `https://your-app.railway.app` |
| `EXPO_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `EXPO_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | `eyJhbGc...` |

### Backend (`backend/.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | ✅ Yes |
| `SUPABASE_KEY` | Supabase anon key | ✅ Yes |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | ✅ Yes |
| `SECRET_KEY` | JWT secret (32+ chars) | ✅ Yes |
| `CORS_ORIGINS` | Allowed origins | ✅ Yes |
| `STRIPE_SECRET_KEY` | Stripe secret key | Optional |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | Optional |

---

## ✨ Features

### User Features
- ✅ User registration and authentication (Supabase Auth)
- ✅ Browse available vehicles
- ✅ Search and filter vehicles
- ✅ Book vehicles for specific dates
- ✅ Digital contract signing
- ✅ KYC document upload
- ✅ Payment processing (Stripe)
- ✅ Loyalty rewards program
- ✅ Review and rate vehicles
- ✅ Booking history
- ✅ Profile management

### Admin Features
- ✅ Vehicle management
- ✅ Booking management
- ✅ User management
- ✅ Contract management
- ✅ Revenue tracking

### Technical Features
- ✅ JWT authentication with Supabase
- ✅ File upload to Supabase Storage
- ✅ RESTful API
- ✅ Real-time updates
- ✅ CORS configuration
- ✅ Error handling
- ✅ API documentation (Swagger)

---

## 📱 Building for Production

### Android APK

```bash
cd mobile

# Preview build (for testing)
eas build --profile preview --platform android

# Production build
eas build --profile production --platform android
```

### iOS IPA

```bash
cd mobile
eas build --profile production --platform ios
```

### Submit to App Stores

```bash
# Android (Google Play)
eas submit --platform android

# iOS (App Store)
eas submit --platform ios
```

---

## 🧪 Testing

### Test Backend Health

```bash
curl https://your-app.railway.app/health
```

**Expected Response:**
```json
{"status":"healthy","environment":"production"}
```

### Test API Documentation

Visit: https://your-app.railway.app/docs

---

## 🐛 Troubleshooting

### Mobile App Won't Connect

**Issue:** "Network request failed"

**Solutions:**
1. Check `EXPO_PUBLIC_API_URL` in `mobile/.env`
2. For Android Emulator, use `http://10.0.2.2:8000`
3. For iOS Simulator, use `http://localhost:8000`
4. For Physical Device, use your computer's IP: `http://192.168.1.XXX:8000`
5. Restart Expo with clear cache: `npx expo start --clear`

### CORS Errors

**Issue:** "CORS policy" errors

**Solution:**
- Set `CORS_ORIGINS=*` in Railway environment variables (for testing)
- For production, specify allowed origins: `CORS_ORIGINS=null,exp://*`

### Authentication Errors

**Issue:** "Invalid authentication credentials"

**Solution:**
- Verify backend uses `auth_supabase.py` for authentication
- Check Supabase credentials are correct
- Ensure mobile app sends JWT token in Authorization header

### Railway Deployment Failed

**Solutions:**
1. Check deployment logs in Railway Dashboard
2. Verify all required environment variables are set
3. Ensure `backend/Procfile` and `backend/runtime.txt` are present
4. Check root directory is set to `backend` in Railway settings

---

## 📚 Additional Documentation

- **Railway Deployment Guide:** `RAILWAY_DEPLOYMENT.md`
- **Supabase Storage Setup:** `SUPABASE_STORAGE_SETUP.md`
- **Backend Setup Guide:** `backend/SETUP_GUIDE.md`
- **Mobile Setup Guide:** `mobile/MOBILE_SETUP.md`

---

## 🔗 Useful Links

- **Supabase Dashboard:** https://supabase.com/dashboard
- **Railway Dashboard:** https://railway.app
- **Expo Documentation:** https://docs.expo.dev
- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **EAS Build:** https://docs.expo.dev/build/introduction/

---

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review documentation in `docs/` folder
3. Check Railway deployment logs
4. Review Expo console logs

---

## 📄 License

This project is proprietary software.

---

## 🎯 Quick Commands Reference

```bash
# Mobile Development
cd mobile
npm install                          # Install dependencies
npx expo start --clear              # Start with clear cache
eas build --profile preview -p android  # Build preview APK

# Backend Development
cd backend
pip install -r requirements.txt     # Install dependencies
uvicorn main:app --reload --port 8000  # Start development server

# Railway Deployment
git add .
git commit -m "Your commit message"
git push origin main                # Auto-deploys to Railway

# EAS Configuration
eas secret:list                     # View EAS secrets
eas build:list                      # View builds
eas submit -p android               # Submit to Play Store
```

---

**Built with ❤️ for Hiya Cars**

**Railway URL:** `https://hiyacars-rental-production.up.railway.app`

**Last Updated:** January 2026
