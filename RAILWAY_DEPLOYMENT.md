# Railway Deployment Guide

Step-by-step guide to deploy the Hiya Cars backend to Railway.

## Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app)
- Supabase project (for database, auth, and storage)
- Code pushed to GitHub repository

## Step 1: Prepare Your Repository

Your backend is already configured for Railway with:
- ✅ `Procfile` - Tells Railway how to start the app
- ✅ `runtime.txt` - Specifies Python 3.10
- ✅ `requirements.txt` - Lists all dependencies

## Step 2: Create Railway Project

### Option A: Deploy from GitHub (Recommended)

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your repository: `hiyacars-rental`
6. Click **"Deploy Now"**

### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to your project
railway link

# Deploy
railway up
```

## Step 3: Configure Root Directory

Railway needs to know your backend is in a subdirectory:

1. Go to your Railway project dashboard
2. Click on your service
3. Go to **"Settings"** tab
4. Scroll to **"Service"** section
5. Find **"Root Directory"**
6. Enter: **`backend`**
7. Click **"Save"**

This tells Railway to build from the `backend` folder.

## Step 4: Add Environment Variables

Go to your service → **"Variables"** tab and add these:

### Required Variables:

```bash
# Supabase (REQUIRED)
SUPABASE_URL=https://wcxmmdujcujrvhwmqyjq.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndjeG1tZHVqY3VqcnZod21xeWpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2MDgzODQsImV4cCI6MjA3ODE4NDM4NH0.nE_benybtak0R8ZXVvBntpwh3qGBB_IK0LFAZp6a7m0
SUPABASE_SERVICE_KEY=your_service_role_key_from_supabase_settings

# JWT (REQUIRED)
SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Settings (REQUIRED)
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com,exp://your-expo-app
PLATFORM_FEE_PERCENTAGE=10.0
```

### Optional Variables (if using these services):

```bash
# Stripe (for payments)
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# OAuth (for social login)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# RTA (for contract submission)
RTA_API_URL=https://api.rta.ae/production
RTA_API_KEY=your_rta_api_key
RTA_ENVIRONMENT=production
```

### How to Get These Values:

#### Supabase Keys:
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_KEY`
   - **service_role** → `SUPABASE_SERVICE_KEY` (⚠️ Keep this secret!)

#### JWT Secret Key:
Generate a secure random string (at least 32 characters):
```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -base64 32
```

#### Stripe Keys:
1. Go to https://dashboard.stripe.com
2. Go to **Developers** → **API keys**
3. Copy your keys (use test keys for testing, live keys for production)

## Step 5: Deploy!

Railway will automatically:
1. ✅ Detect it's a Python project
2. ✅ Read `runtime.txt` for Python version (3.10)
3. ✅ Install dependencies from `requirements.txt`
4. ✅ Run the command from `Procfile`
5. ✅ Assign a public URL

## Step 6: Get Your Deployment URL

After successful deployment:

1. Go to your service in Railway dashboard
2. Click **"Settings"** tab
3. Scroll to **"Domains"** section
4. You'll see a URL like: `https://hiyacars-rental-production.up.railway.app`
5. Click **"Generate Domain"** if no domain is shown

**Copy this URL!** You'll need it for your mobile app.

## Step 7: Test Your Deployment

### Test API Health:

```bash
curl https://your-app.railway.app/health
```

### Test API Documentation:

Visit in browser:
```
https://your-app.railway.app/docs
```

You should see the FastAPI Swagger UI.

### Test Authentication:

```bash
curl -X POST https://your-app.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User",
    "phone": "+971501234567"
  }'
```

## Step 8: Update Mobile App

Update your mobile app's API URL:

### For Development (.env):
```env
EXPO_PUBLIC_API_URL=https://your-app.railway.app
```

### For Production Build (EAS):
```bash
eas secret:create --scope project --name EXPO_PUBLIC_API_URL --value "https://your-app.railway.app"
```

### Update CORS:

Make sure your Railway backend allows requests from your mobile app:

In Railway Variables, update `CORS_ORIGINS`:
```
CORS_ORIGINS=https://your-frontend.com,exp://your-expo-app
```

For development, you can temporarily use:
```
CORS_ORIGINS=*
```

## Step 9: Set Up Supabase Storage

Don't forget to set up storage buckets! Follow `SUPABASE_STORAGE_SETUP.md`:

1. Create buckets: `avatars`, `kyc-documents`, `vehicle-images`, `contracts`
2. Configure RLS policies
3. Test uploads from your deployed API

## Monitoring & Logs

### View Logs:

In Railway dashboard:
1. Go to your service
2. Click **"Deployments"** tab
3. Click on latest deployment
4. View logs in real-time

### View Metrics:

1. Go to **"Metrics"** tab
2. See CPU, memory, network usage

## Automatic Redeployment

Railway automatically redeploys when you push to GitHub:

```bash
git add .
git commit -m "Update backend"
git push origin main
```

Railway will detect the push and redeploy automatically!

## Troubleshooting

### Build Failed

**Check build logs** in Railway dashboard:
- Look for Python version issues
- Check for missing dependencies
- Verify `requirements.txt` is correct

### Service Crashed

**Common issues:**
1. Missing environment variables
2. Database connection issues (check Supabase URL)
3. Port binding (Railway provides `$PORT` automatically)

### Can't Connect from Mobile App

1. **Check CORS**: Make sure mobile app origin is in `CORS_ORIGINS`
2. **Check URL**: Verify you're using the correct Railway URL
3. **Check logs**: Look for incoming requests in Railway logs

### File Uploads Not Working

1. **Check Supabase buckets**: Verify buckets are created
2. **Check RLS policies**: Ensure proper access control
3. **Check credentials**: Verify `SUPABASE_SERVICE_KEY` is set

## Cost Estimation

### Railway Pricing:

- **Free Tier**: $5 credit/month (limited resources)
- **Hobby Plan**: $5/month + usage
- **Pro Plan**: $20/month + usage

### Typical Backend Cost:

Small app (< 1000 users):
- Railway: ~$5-10/month
- Supabase: Free tier (up to 500MB database, 1GB storage)

**Total: ~$5-10/month**

## Production Checklist

Before going live:

- [ ] Set `DEBUG=False`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use production Stripe keys
- [ ] Use production RTA credentials
- [ ] Set proper CORS origins (no wildcards)
- [ ] Set up Supabase Storage buckets
- [ ] Configure RLS policies
- [ ] Test all endpoints
- [ ] Test file uploads
- [ ] Set up monitoring
- [ ] Set up error tracking (Sentry)

## Next Steps

1. ✅ Backend deployed to Railway
2. ✅ Environment variables configured
3. ✅ Supabase Storage set up
4. 📱 Update mobile app API URL
5. 📱 Test mobile app with production backend
6. 📱 Build production APK/IPA
7. 🚀 Submit to app stores

## Support

- **Railway Docs**: https://docs.railway.app
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

**Your Railway URL**: `_______________________________`

**Deployment Date**: `_______________________________`

