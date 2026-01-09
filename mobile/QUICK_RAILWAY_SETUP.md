# 🚀 Quick Railway Setup Guide

## 1️⃣ Get Railway URL
```
Go to Railway Dashboard → Your Service → Settings → Domains
Copy URL: https://your-app.railway.app
```

## 2️⃣ Update Local .env File
```env
# Edit mobile/.env
EXPO_PUBLIC_API_URL=https://your-app.railway.app
```

## 3️⃣ Restart Expo
```bash
cd mobile
npm start -- --clear
```

## 4️⃣ Set EAS Secret (for production builds)
```bash
cd mobile
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-app.railway.app"
```

## 5️⃣ Update Railway CORS
```
Railway Dashboard → Your Service → Variables → CORS_ORIGINS
```

Set to:
```
CORS_ORIGINS=*
```

Or for production:
```
CORS_ORIGINS=null,exp://*
```

## 6️⃣ Build Production
```bash
# Preview APK
eas build --profile preview --platform android

# Production
eas build --profile production --platform android
```

---

## ✅ Done!

Your mobile app is now connected to Railway! 🎉

See `RAILWAY_MOBILE_SETUP.md` for detailed instructions.
