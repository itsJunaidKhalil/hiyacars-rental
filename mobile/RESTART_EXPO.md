# 🔄 How to Restart Expo to Pick Up Environment Changes

## ⚠️ Important:
Pressing `r` to reload **does NOT** reload environment variables!

## ✅ Correct Way to Restart:

### Step 1: Stop Expo
In your Expo terminal, press:
```
Ctrl+C
```

### Step 2: Restart with Clear Cache
```bash
npm start -- --clear
```

### Step 3: Wait for Startup
You should see:
```
env: load .env
env: export EXPO_PUBLIC_API_URL EXPO_PUBLIC_SUPABASE_URL EXPO_PUBLIC_SUPABASE_ANON_KEY
```

### Step 4: Reload App on Device
Once Expo is ready, press `a` for Android or open on your device

---

## 🔍 Verify Environment Variables Loaded

After restart, you should see in the Expo terminal:
```
env: load .env
env: export EXPO_PUBLIC_API_URL EXPO_PUBLIC_SUPABASE_URL EXPO_PUBLIC_SUPABASE_ANON_KEY
```

This confirms your new API URL (`http://192.168.1.101:8000`) is loaded!

---

## ✅ Expected Result

After full restart:
- ✅ No more "Network request failed" errors
- ✅ Backend logs show incoming requests
- ✅ User sync succeeds
- ✅ Vehicles load successfully

---

## 📝 Remember:

| Change Type | Action Required |
|-------------|-----------------|
| Code changes | Press `r` (reload) |
| Environment variables (.env) | Full restart (Ctrl+C + npm start) |
| Package installation | Full restart |

---

**Do this now:** Press `Ctrl+C` in Terminal 4, then run `npm start -- --clear`
