# 🚀 Connect Mobile App to Railway Backend

Your backend is deployed! Now let's connect your mobile app to it.

---

## 📋 Step-by-Step Guide

### ✅ **Step 1: Get Your Railway URL**

1. Go to https://railway.app
2. Open your `hiyacars-rental` project
3. Click on your backend service
4. Go to **Settings** tab
5. Scroll to **Domains** section
6. Copy your deployment URL

**Example:** `https://hiyacars-rental-production.up.railway.app`

**📝 Write it here:** `_______________________________________`

---

### ✅ **Step 2: Update Mobile App .env File**

Update `mobile/.env` with your Railway URL:

```bash
cd mobile
```

Then edit the `.env` file:

```env
# API Configuration - Railway Production Backend
EXPO_PUBLIC_API_URL=https://your-railway-url.railway.app

# Supabase Configuration (keep these the same)
EXPO_PUBLIC_SUPABASE_URL=https://wcxmmdujcujrvhwmqyjq.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Replace `https://your-railway-url.railway.app` with your actual Railway URL!**

---

### ✅ **Step 3: Update CORS on Railway**

Your Railway backend needs to allow requests from your mobile app.

1. Go to Railway Dashboard
2. Click on your backend service
3. Go to **Variables** tab
4. Find `CORS_ORIGINS` variable (or add it if not there)
5. Update the value:

**For Testing:**
```
CORS_ORIGINS=*
```

**For Production (Recommended):**
```
CORS_ORIGINS=null,exp://*,https://your-frontend-domain.com
```

6. Click **Save** or **Update**
7. Wait 1-2 minutes for Railway to redeploy

---

### ✅ **Step 4: Restart Your Mobile App**

In Terminal 4 (where Expo is running):

1. Press `Ctrl+C` to stop Expo
2. Restart with:
   ```bash
   npx expo start --clear
   ```

**Look for this in the logs:**
```
env: load .env
env: export EXPO_PUBLIC_API_URL
```

**And then:**
```
LOG  🔗 API_BASE_URL: https://your-railway-url.railway.app
```

---

### ✅ **Step 5: Test the Connection**

1. Wait for Expo to start
2. Press `r` to reload the app on your device
3. Watch the console logs

**Expected Output:**
```
✅ LOG  🔗 API_BASE_URL: https://your-railway-url.railway.app
✅ LOG  Syncing user with backend...
✅ LOG  User synced successfully
✅ LOG  Vehicles fetched
```

**Check Railway Logs:**
1. Railway Dashboard → Your Service → Deployments
2. Click latest deployment
3. You should see incoming requests:
   ```
   INFO: "GET /api/v1/vehicles/" 200 OK
   INFO: "POST /api/v1/auth/..." 200 OK
   ```

---

### ✅ **Step 6: Set EAS Secret for Production Builds**

For production APK/IPA builds, set the EAS secret:

```bash
cd mobile
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-railway-url.railway.app"
```

**Verify:**
```bash
eas secret:list
```

**Expected:**
```
✔ EXPO_PUBLIC_API_URL: https://your-railway-url.railway.app
```

---

## 🧪 Testing Checklist

After completing the steps above:

- [ ] Mobile `.env` updated with Railway URL
- [ ] Railway `CORS_ORIGINS` updated to `*` or includes `null`
- [ ] Expo restarted with clear cache
- [ ] Console shows Railway URL in logs
- [ ] No "Network request failed" errors
- [ ] Railway logs show incoming requests
- [ ] App functions work (login, vehicles, etc.)
- [ ] EAS secret created

---

## 🐛 Troubleshooting

### Issue: "Network request failed"

**Solutions:**
1. Verify Railway URL is correct in `.env`
2. Check Railway service is running (not crashed)
3. Verify `CORS_ORIGINS=*` in Railway
4. Restart Expo completely
5. Check Railway logs for errors

### Issue: CORS Error

**Solution:**
1. Go to Railway → Variables
2. Set `CORS_ORIGINS=*`
3. Wait for redeploy (~1-2 minutes)
4. Restart mobile app

### Issue: "Invalid authentication credentials"

**This is a different issue** - the connection works, but there's an auth mismatch. This needs backend investigation, not a connection fix.

### Issue: Railway Service Crashed

**Solutions:**
1. Check Railway logs for errors
2. Verify all environment variables are set
3. Check Supabase credentials are correct
4. Redeploy the service

---

## 📊 Connection Flow

```
┌─────────────────────┐
│  Mobile App         │
│  (Your Device)      │
└──────────┬──────────┘
           │
           │ HTTPS (Port 443)
           │ https://your-app.railway.app
           ▼
┌─────────────────────┐
│  Railway            │
│  (FastAPI Backend)  │
└──────────┬──────────┘
           │
           │ Database Queries
           ▼
┌─────────────────────┐
│  Supabase           │
│  (PostgreSQL + Auth)│
└─────────────────────┘
```

---

## 🎯 Quick Commands

```bash
# Update mobile .env (manual edit)
cd mobile
# Edit .env file with Railway URL

# Restart Expo
npx expo start --clear

# Set EAS secret
cd mobile
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-url.railway.app"

# View EAS secrets
eas secret:list

# Test Railway backend
curl https://your-railway-url.railway.app/health

# View Railway logs
# Go to Railway Dashboard → Service → Deployments → Latest
```

---

## 🚀 Production Deployment Checklist

Before building production APK/IPA:

- [ ] Railway backend is deployed and running
- [ ] All Railway environment variables are set correctly
- [ ] `CORS_ORIGINS` is properly configured (not `*` in production)
- [ ] Mobile `.env` points to Railway URL
- [ ] EAS secret is created with Railway URL
- [ ] App tested thoroughly with Railway backend
- [ ] All features work (auth, vehicles, bookings, etc.)
- [ ] File uploads work correctly
- [ ] No console errors

---

## 📱 Building Production APK/IPA

Once everything is working:

```bash
cd mobile

# Preview build (for testing)
eas build --profile preview --platform android

# Production build
eas build --profile production --platform android
eas build --profile production --platform ios

# View builds
eas build:list
```

---

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ Console shows Railway URL: `https://your-app.railway.app`
2. ✅ No "Network request failed" errors
3. ✅ Railway logs show incoming requests
4. ✅ App functions work correctly
5. ✅ You can login/register
6. ✅ Vehicles load
7. ✅ All features work

---

## 🎉 Next Steps

After successful connection:

1. ✅ Test all app features thoroughly
2. ✅ Fix authentication issue (if still present)
3. ✅ Build preview APK for testing
4. ✅ Test on multiple devices
5. ✅ Build production APK/IPA
6. 🚀 Submit to app stores!

---

**Your Railway URL:** `_______________________________________`

**Date Connected:** `_______________________________________`

**Status:** [ ] Testing [ ] Ready for Production [ ] In Production

---

Good luck! 🚀
