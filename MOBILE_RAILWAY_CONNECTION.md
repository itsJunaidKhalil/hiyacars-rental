# 🔗 Mobile App ↔️ Railway Backend Connection Guide

This document explains how to connect your Hiya Cars mobile app to the Railway-deployed backend.

---

## 🎯 Overview

```
┌─────────────────┐
│  Mobile App     │
│  (Expo/React    │
│   Native)       │
└────────┬────────┘
         │
         │ HTTPS Requests
         │ (with CORS)
         ▼
┌─────────────────┐
│  Railway        │
│  Backend        │
│  (FastAPI)      │
└────────┬────────┘
         │
         │ Database
         ▼
┌─────────────────┐
│  Supabase       │
│  (PostgreSQL +  │
│   Storage)      │
└─────────────────┘
```

---

## 📝 Step-by-Step Implementation

### ✅ STEP 1: Get Your Railway URL

**Where:** Railway Dashboard  
**Action:** Copy your backend deployment URL

```
Example: https://hiyacars-rental-production.up.railway.app
```

**How to find it:**
1. Go to https://railway.app
2. Open your project
3. Click on backend service
4. Settings → Domains
5. Copy the URL (or click "Generate Domain" if none exists)

---

### ✅ STEP 2: Update Mobile App .env File

**File:** `mobile/.env`  
**Action:** Set the API URL

```env
EXPO_PUBLIC_API_URL=https://hiyacars-rental-production.up.railway.app
```

**📍 Location:** `/hiyacars-rental/mobile/.env`

**For different environments:**

```env
# Development (Local Backend)
EXPO_PUBLIC_API_URL=http://localhost:8000          # iOS Simulator
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000          # Android Emulator
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000     # Physical Device

# Production (Railway Backend)
EXPO_PUBLIC_API_URL=https://your-app.railway.app
```

---

### ✅ STEP 3: Restart Your Mobile App

**Terminal:**
```bash
cd mobile
npm start -- --clear
```

**This will:**
- Clear cache
- Reload environment variables
- Connect to new API URL

---

### ✅ STEP 4: Set EAS Secret (For Production Builds)

**When:** Building production APK/IPA  
**Tool:** EAS CLI

```bash
# Install EAS CLI (if needed)
npm install -g eas-cli

# Login
eas login

# Navigate to mobile directory
cd mobile

# Create secret
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-app.railway.app"

# Verify
eas secret:list
```

**Why?** Production builds don't use `.env` files. They use EAS secrets instead.

---

### ✅ STEP 5: Update Railway CORS Settings

**Where:** Railway Dashboard → Variables  
**Variable:** `CORS_ORIGINS`

**For Testing:**
```
CORS_ORIGINS=*
```

**For Production:**
```
CORS_ORIGINS=null,exp://*,https://your-frontend-domain.com
```

**Explanation:**
- `*` = Allow all origins (⚠️ only for testing)
- `null` = Allow mobile apps (they send null origin)
- `exp://*` = Allow Expo development clients

**After updating:**
1. Click "Update" or "Save"
2. Railway auto-redeploys (~1-2 minutes)
3. Your mobile app can now make requests!

---

## 🔍 How It Works

### Development Mode

```javascript
// mobile/constant/api.js

1. Reads EXPO_PUBLIC_API_URL from .env file
   ↓
2. Constants.expoConfig.extra.EXPO_PUBLIC_API_URL
   ↓
3. Returns API URL
   ↓
4. All API endpoints use this URL
```

### Production Mode

```
1. EAS Build reads secrets during build
   ↓
2. Injects EXPO_PUBLIC_API_URL into app bundle
   ↓
3. App uses the injected URL at runtime
   ↓
4. Makes requests to Railway backend
```

---

## 🧪 Testing Your Setup

### Test 1: Check API URL in App

Add this to your app temporarily:

```javascript
import { API_BASE_URL } from './constant/api';
console.log('API URL:', API_BASE_URL);
```

**Expected output:**
```
API URL: https://your-app.railway.app
```

### Test 2: Make a Test Request

```bash
# Test Railway backend is running
curl https://your-app.railway.app/health

# Expected response:
{"status":"ok"}
```

### Test 3: Try Login/Register

1. Open mobile app
2. Try to register/login
3. Check Expo console for API requests
4. Check Railway logs for incoming requests

### Test 4: Check Railway Logs

**Railway Dashboard:**
1. Your Service → Deployments
2. Click latest deployment
3. View logs

**Look for:**
```
INFO: 192.168.1.1:12345 - "POST /api/v1/auth/login HTTP/1.1" 200 OK
```

---

## ❌ Common Issues & Solutions

### Issue 1: "Network request failed"

**Symptoms:**
- Mobile app can't connect to backend
- All API requests fail

**Solutions:**
```bash
# 1. Verify Railway URL is correct
echo $EXPO_PUBLIC_API_URL

# 2. Test Railway endpoint
curl https://your-app.railway.app/health

# 3. Clear cache and restart
npm start -- --clear

# 4. Check Railway service is running
# Go to Railway Dashboard and check deployment status
```

### Issue 2: CORS Error

**Symptoms:**
- Error: "has been blocked by CORS policy"
- Requests fail with CORS errors in console

**Solutions:**
1. Update `CORS_ORIGINS` in Railway to `*` or `null`
2. Save and wait for Railway to redeploy
3. Restart mobile app

### Issue 3: Android Emulator Can't Connect to Localhost

**Symptoms:**
- iOS works, Android doesn't
- Using local backend on `localhost:8000`

**Solution:**
Android emulator can't access `localhost`. Use `10.0.2.2` instead:

```env
# In .env
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
```

### Issue 4: Production Build Not Connecting

**Symptoms:**
- Dev version works
- Production APK/IPA doesn't connect

**Solutions:**
```bash
# 1. Check EAS secret exists
eas secret:list

# 2. If missing, create it
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-app.railway.app"

# 3. Rebuild the app
eas build --profile production --platform android
```

### Issue 5: Environment Variable Not Loading

**Symptoms:**
- API URL is undefined
- Falls back to default URL

**Solutions:**
1. Make sure `.env` file exists in `mobile/` folder
2. Restart Expo: `npm start -- --clear`
3. Check `app.json` has the extra config
4. Verify `babel.config.js` has dotenv plugin

---

## 📦 Files Changed/Created

### Created:
- ✅ `mobile/.env` - Environment variables
- ✅ `mobile/RAILWAY_MOBILE_SETUP.md` - Detailed guide
- ✅ `mobile/QUICK_RAILWAY_SETUP.md` - Quick reference
- ✅ `MOBILE_RAILWAY_CONNECTION.md` - This file

### Modified:
- ✅ `mobile/constant/api.js` - Uses environment variables
- ✅ `mobile/app.json` - Added EXPO_PUBLIC_API_URL to extra
- ✅ `mobile/.gitignore` - Added .env to ignore list

### Already Configured:
- ✅ `mobile/babel.config.js` - Already has react-native-dotenv
- ✅ `mobile/eas.json` - Already configured for EAS builds

---

## 🎯 Production Deployment Checklist

Before deploying to production:

- [ ] Railway backend is deployed and running
- [ ] Railway URL is accessible (test with curl)
- [ ] All Railway environment variables are set
- [ ] Supabase is configured and working
- [ ] `.env` file updated with Railway URL
- [ ] Mobile app tested with Railway backend
- [ ] EAS secret created for production
- [ ] CORS properly configured (no wildcards in production)
- [ ] Test registration works
- [ ] Test login works
- [ ] Test file uploads work
- [ ] Build production APK/IPA
- [ ] Test production build before app store submission

---

## 🚀 Quick Commands

```bash
# Development
cd mobile
npm start -- --clear

# View current environment
eas secret:list

# Build preview (APK)
eas build --profile preview --platform android

# Build production
eas build --profile production --platform android
eas build --profile production --platform ios

# View builds
eas build:list

# Test Railway backend
curl https://your-app.railway.app/health
curl https://your-app.railway.app/docs
```

---

## 📚 Documentation Links

- **Railway Deployment:** See `RAILWAY_DEPLOYMENT.md`
- **Mobile Setup:** See `mobile/RAILWAY_MOBILE_SETUP.md`
- **Quick Start:** See `mobile/QUICK_RAILWAY_SETUP.md`
- **Railway Docs:** https://docs.railway.app
- **EAS Build:** https://docs.expo.dev/build/introduction/
- **Expo Environment Variables:** https://docs.expo.dev/guides/environment-variables/

---

## 💡 Pro Tips

1. **Use different .env files for different environments:**
   - `.env.development` for local backend
   - `.env.production` for Railway backend

2. **Test with Railway before building production:**
   - Update `.env` to Railway URL
   - Test thoroughly in dev mode
   - Then build production

3. **Monitor Railway logs while testing:**
   - Keep Railway dashboard open
   - Watch logs in real-time
   - Catch errors immediately

4. **Keep secrets secure:**
   - Never commit `.env` to git
   - Use EAS secrets for production
   - Rotate secrets regularly

---

**Your Railway URL:** `_______________________________`

**Setup Date:** `_______________________________`

**Tested By:** `_______________________________`

---

✅ **Setup Complete!** Your mobile app is now connected to Railway! 🎉
