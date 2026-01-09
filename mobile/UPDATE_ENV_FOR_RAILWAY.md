# 🚀 Quick Fix: Connect to Railway Backend

## Current Issue:
Your app is trying to connect to `http://localhost:8000` but the local backend isn't running.

## Solution: Use Railway Backend

### Step 1: Get Your Railway URL
1. Go to https://railway.app
2. Open your project
3. Click on your backend service
4. Go to **Settings** → **Domains**
5. Copy your URL (e.g., `https://hiyacars-rental-production.up.railway.app`)

### Step 2: Update mobile/.env

Replace:
```env
EXPO_PUBLIC_API_URL=http://localhost:8000
```

With:
```env
EXPO_PUBLIC_API_URL=https://your-railway-url.railway.app
```

### Step 3: Restart Expo

Press `r` in the Expo terminal or:
```bash
npm start -- --clear
```

### Step 4: Update CORS on Railway

Don't forget to set `CORS_ORIGINS=*` in Railway:
1. Railway Dashboard → Your Service → Variables
2. Find or add `CORS_ORIGINS`
3. Set value to: `*`
4. Save and wait for redeploy

## ✅ Done!

Your app should now connect to Railway successfully!
