# Mobile App Setup for Railway Backend

This guide explains how to connect your mobile app to the Railway-deployed backend (Step 8 of Railway Deployment).

## 📋 What We've Done

✅ Created `.env` file for local development  
✅ Updated `api.js` to use environment variables  
✅ Configured `babel.config.js` for environment variables  
✅ Updated `app.json` for Expo environment variables  

## 🚀 Step-by-Step Guide

### 1. Get Your Railway Deployment URL

First, you need your Railway backend URL:

1. Go to [Railway Dashboard](https://railway.app)
2. Open your project
3. Click on your backend service
4. Go to **Settings** tab
5. Scroll to **Domains** section
6. Copy the URL (e.g., `https://hiyacars-rental-production.up.railway.app`)

**📝 Note:** If you don't see a domain, click **"Generate Domain"** first.

---

### 2. Update Local Development Environment

Update your `.env` file in the `mobile` folder:

```env
# Replace with your actual Railway URL
EXPO_PUBLIC_API_URL=https://your-app.railway.app
```

**For different development scenarios:**

```env
# For Android Emulator (local backend)
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000

# For iOS Simulator (local backend)
EXPO_PUBLIC_API_URL=http://localhost:8000

# For Physical Device (local backend on same network)
EXPO_PUBLIC_API_URL=http://192.168.1.XXX:8000

# For Railway Production Backend
EXPO_PUBLIC_API_URL=https://your-app.railway.app
```

---

### 3. Test Local Development

Restart your Expo development server:

```bash
cd mobile
npm start -- --clear
```

The app should now connect to your Railway backend!

**Verify the connection:**
- Try logging in or registering
- Check the Expo console for API requests
- Check Railway logs for incoming requests

---

### 4. Set Up EAS Secrets for Production Builds

For production builds (APK/IPA), you need to set EAS secrets:

#### Install EAS CLI (if not installed):

```bash
npm install -g eas-cli
```

#### Login to EAS:

```bash
eas login
```

#### Create the API URL Secret:

```bash
cd mobile
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-app.railway.app"
```

**Replace `https://your-app.railway.app` with your actual Railway URL!**

#### Verify the Secret:

```bash
eas secret:list
```

You should see:
```
✔ EXPO_PUBLIC_API_URL: https://your-app.railway.app
```

---

### 5. Update CORS on Railway Backend

Your Railway backend needs to allow requests from your mobile app.

#### Go to Railway Dashboard:

1. Open your Railway project
2. Click on your backend service
3. Go to **Variables** tab
4. Find `CORS_ORIGINS` variable

#### Update CORS_ORIGINS:

**For Development (Testing):**
```
CORS_ORIGINS=*
```

**For Production (Recommended):**
```
CORS_ORIGINS=exp://192.168.1.1,exp://*,https://your-frontend.com
```

**Explanation:**
- `exp://*` - Allows Expo development clients
- `*` - Allows all origins (⚠️ Use only for testing!)

#### For React Native Mobile Apps:

Most mobile apps use `null` origin, so you might need:

```
CORS_ORIGINS=null,exp://*,https://your-frontend.com
```

#### After updating:

1. Click **"Save"** or **"Update"**
2. Railway will automatically redeploy with new CORS settings
3. Wait 1-2 minutes for deployment

---

### 6. Build Production APK/IPA

Now you can build production versions:

#### Preview Build (APK for testing):

```bash
cd mobile
eas build --profile preview --platform android
```

#### Production Build:

```bash
# Android (AAB for Play Store)
eas build --profile production --platform android

# iOS (for App Store)
eas build --profile production --platform ios
```

The build will automatically use the `EXPO_PUBLIC_API_URL` secret you set earlier!

---

### 7. Verify Everything Works

#### Test Checklist:

- [ ] ✅ Mobile app connects to Railway backend
- [ ] ✅ User registration works
- [ ] ✅ User login works
- [ ] ✅ API requests are successful
- [ ] ✅ No CORS errors in console
- [ ] ✅ Images/files upload correctly

#### Check Railway Logs:

1. Go to Railway Dashboard
2. Click your service
3. Go to **Deployments** tab
4. Click latest deployment
5. View logs for incoming requests

You should see requests like:
```
INFO:     192.168.1.1:12345 - "POST /api/v1/auth/login HTTP/1.1" 200 OK
```

---

## 🔧 Troubleshooting

### Issue: "Network request failed"

**Solution:**
1. Check your Railway URL is correct in `.env`
2. Make sure Railway deployment is running
3. Test the API manually: `curl https://your-app.railway.app/health`

### Issue: CORS Error

**Solution:**
1. Update `CORS_ORIGINS` in Railway to include `*` or `null`
2. Wait for Railway to redeploy
3. Clear mobile app cache: `npm start -- --clear`

### Issue: "Cannot connect to server"

**Solution:**
1. Verify Railway service is running (not crashed)
2. Check Railway logs for errors
3. Verify all environment variables are set in Railway
4. Make sure Railway domain is generated

### Issue: Production build not connecting

**Solution:**
1. Verify EAS secret is set: `eas secret:list`
2. Rebuild the app after setting secrets
3. Check the Railway URL doesn't have trailing slash

### Issue: Android Emulator can't connect

**Solution:**
For local backend, use `http://10.0.2.2:8000` instead of `localhost:8000`

Update `.env`:
```env
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
```

---

## 📱 Environment Variables Reference

### Development (.env file):

```env
# Local Backend
EXPO_PUBLIC_API_URL=http://localhost:8000

# Railway Backend
EXPO_PUBLIC_API_URL=https://your-app.railway.app
```

### Production (EAS Secrets):

```bash
# Set once, used for all production builds
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-app.railway.app"
```

### Update EAS Secret:

```bash
# Delete old secret
eas secret:delete --name EXPO_PUBLIC_API_URL

# Create new secret
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://new-url.railway.app"
```

---

## 🎯 Quick Commands Reference

```bash
# Start development server
npm start -- --clear

# Build preview APK
eas build --profile preview --platform android

# Build production
eas build --profile production --platform all

# View EAS secrets
eas secret:list

# View EAS builds
eas build:list

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

---

## ✅ Next Steps

1. ✅ Update `.env` with Railway URL
2. ✅ Test app with Railway backend
3. ✅ Set EAS secret for production
4. ✅ Update CORS on Railway
5. ✅ Build production APK/IPA
6. ✅ Test production build
7. 🚀 Submit to app stores!

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Expo Environment Variables](https://docs.expo.dev/guides/environment-variables/)
- [EAS Build Documentation](https://docs.expo.dev/build/introduction/)
- [EAS Secrets Documentation](https://docs.expo.dev/build-reference/variables/)

---

**Your Railway URL:** `_______________________________`

**Last Updated:** `_______________________________`
