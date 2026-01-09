# Supabase Storage Setup Guide

This guide will help you set up Supabase Storage buckets for the Hiya Cars Rental app.

## Overview

The app has been configured to use **Supabase Storage** instead of AWS S3 for all file uploads:
- ✅ User profile pictures (avatars)
- ✅ KYC verification documents
- ✅ Vehicle images
- ✅ Contracts and signatures

## Benefits of Using Supabase Storage

- **Already Integrated**: You're using Supabase for auth and database
- **Free Tier**: 1GB storage + 2GB bandwidth/month
- **Built-in CDN**: Fast file delivery worldwide
- **Access Control**: Integrates with Supabase auth and RLS
- **Simpler Setup**: No AWS credentials needed

---

## Step 1: Create Storage Buckets

### 1. Go to Supabase Dashboard

1. Visit: https://supabase.com/dashboard
2. Select your project: `wcxmmdujcujrvhwmqyjq`
3. Click **"Storage"** in the left sidebar

### 2. Create Buckets

Create the following buckets by clicking **"New bucket"**:

#### Bucket 1: `avatars`
- **Name**: `avatars`
- **Public**: ✅ Yes (allow public access)
- **File size limit**: 2MB
- **Allowed MIME types**: `image/*`

#### Bucket 2: `kyc-documents`
- **Name**: `kyc-documents`
- **Public**: ❌ No (private - authenticated users only)
- **File size limit**: 10MB
- **Allowed MIME types**: `image/*,application/pdf`

#### Bucket 3: `vehicle-images`
- **Name**: `vehicle-images`
- **Public**: ✅ Yes (allow public access)
- **File size limit**: 5MB
- **Allowed MIME types**: `image/*`

#### Bucket 4: `contracts`
- **Name**: `contracts`
- **Public**: ❌ No (private - authenticated users only)
- **File size limit**: 10MB
- **Allowed MIME types**: `application/pdf`

---

## Step 2: Configure Bucket Policies (RLS)

### For Public Buckets (`avatars`, `vehicle-images`)

1. Click on the bucket name
2. Go to **"Policies"** tab
3. Click **"New Policy"**
4. Select **"For full customization"**

#### Policy 1: Allow Public Read

```sql
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING ( bucket_id = 'avatars' );
```

#### Policy 2: Allow Authenticated Upload

```sql
CREATE POLICY "Authenticated users can upload"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'avatars' 
  AND auth.role() = 'authenticated'
);
```

#### Policy 3: Allow Users to Update Their Own Files

```sql
CREATE POLICY "Users can update own files"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'avatars' 
  AND auth.uid()::text = (storage.foldername(name))[1]
)
WITH CHECK (
  bucket_id = 'avatars' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);
```

#### Policy 4: Allow Users to Delete Their Own Files

```sql
CREATE POLICY "Users can delete own files"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'avatars' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);
```

**Repeat similar policies for `vehicle-images` bucket** (replace 'avatars' with 'vehicle-images')

---

### For Private Buckets (`kyc-documents`, `contracts`)

#### Policy 1: Authenticated Users Can Upload

```sql
CREATE POLICY "Authenticated users can upload KYC"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'kyc-documents' 
  AND auth.role() = 'authenticated'
);
```

#### Policy 2: Users Can Read Their Own Files

```sql
CREATE POLICY "Users can read own KYC documents"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'kyc-documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);
```

#### Policy 3: Admins Can Read All Files

```sql
CREATE POLICY "Admins can read all KYC documents"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'kyc-documents' 
  AND EXISTS (
    SELECT 1 FROM public.users
    WHERE id = auth.uid()
    AND role IN ('org_admin', 'support')
  )
);
```

**Repeat similar policies for `contracts` bucket** (replace 'kyc-documents' with 'contracts')

---

## Step 3: Quick Policy Setup (Alternative Method)

Instead of writing SQL, you can use Supabase's policy templates:

1. Click on bucket → **"Policies"** tab
2. Click **"New Policy"**
3. Select from templates:
   - **"Allow public access"** for `avatars` and `vehicle-images`
   - **"Allow authenticated access"** for `kyc-documents` and `contracts`

---

## Step 4: Test Storage Setup

### Test from Supabase Dashboard

1. Go to Storage → Select a bucket
2. Try uploading a test file
3. Click on the file → Copy public URL
4. Open URL in browser to verify access

### Test from Mobile App

The mobile app includes helper functions in `mobile/services/storage.js`:

```javascript
import { uploadAvatar, uploadKYCDocument, uploadVehicleImage } from './services/storage';

// Upload avatar
const avatarUrl = await uploadAvatar(userId, imagePickerResult);

// Upload KYC document
const kycUrl = await uploadKYCDocument(userId, 'emirates_id', 'front', imagePickerResult);

// Upload vehicle image
const vehicleUrl = await uploadVehicleImage(vehicleId, imagePickerResult);
```

---

## Step 5: Update Backend Environment Variables

The backend already uses Supabase credentials. Make sure these are set in Railway:

```bash
SUPABASE_URL=https://wcxmmdujcujrvhwmqyjq.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
```

**You no longer need AWS credentials!** These can be removed:
- ~~AWS_ACCESS_KEY_ID~~
- ~~AWS_SECRET_ACCESS_KEY~~
- ~~AWS_BUCKET_NAME~~
- ~~AWS_REGION~~

---

## File Organization Structure

### Avatars
```
avatars/
  └── {user_id}/
      └── avatar.jpg
```

### KYC Documents
```
kyc-documents/
  └── {user_id}/
      ├── emirates_id/
      │   ├── front.jpg
      │   └── back.jpg
      ├── passport/
      │   ├── front.jpg
      │   └── back.jpg
      ├── driving_license/
      │   ├── front.jpg
      │   └── back.jpg
      └── signatures/
          └── signature_123.jpg
```

### Vehicle Images
```
vehicle-images/
  └── {vehicle_id}/
      ├── image_1.jpg
      ├── image_2.jpg
      └── image_3.jpg
```

### Contracts
```
contracts/
  └── {booking_id}/
      ├── rental_contract.pdf
      └── signed_contract.pdf
```

---

## API Endpoints Using Storage

### Backend Endpoints

#### Upload Avatar
```http
POST /api/v1/auth/me/avatar
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: (image file)
```

#### Upload KYC Document
```http
POST /api/v1/kyc/documents/{document_type}?side=front
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: (image file)
```

#### Upload Vehicle Image
```http
POST /api/v1/vehicles/{vehicle_id}/images
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: (image file)
```

---

## Troubleshooting

### Error: "Bucket not found"

**Solution**: Create the bucket in Supabase dashboard:
1. Go to Storage → New bucket
2. Enter bucket name exactly as shown above
3. Set public/private access

### Error: "Not allowed to perform this action"

**Solution**: Add proper RLS policies:
1. Go to Storage → Select bucket → Policies
2. Add policies from Step 2 above
3. Make sure authenticated users have INSERT permission

### Error: "File already exists"

**Solution**: The app is set to not overwrite files. Either:
- Delete the existing file first
- Change `upsert: false` to `upsert: true` in `mobile/services/storage.js`

### Error: "Row Level Security is not enabled"

**Solution**: Enable RLS on storage.objects table:
1. Go to Storage → Settings
2. Enable "Row Level Security"
3. Add policies as described above

---

## Storage Limits

### Free Plan
- **Storage**: 1GB
- **Bandwidth**: 2GB/month
- **File uploads**: Unlimited count

### Pro Plan ($25/month)
- **Storage**: 100GB
- **Bandwidth**: 200GB/month
- **File uploads**: Unlimited count

### Recommendations
- **Compress images** before upload (done automatically in mobile app)
- **Delete old files** periodically
- **Use image optimization** services if needed

---

## Next Steps

1. ✅ Create all 4 buckets in Supabase dashboard
2. ✅ Set up RLS policies for each bucket
3. ✅ Test uploading files from Supabase dashboard
4. ✅ Deploy backend to Railway (already done)
5. ✅ Update mobile app API URL to point to Railway
6. ✅ Test file uploads from mobile app

---

## Support

If you encounter issues:
1. Check Supabase logs: Dashboard → Logs → Storage
2. Check browser console for errors
3. Verify bucket names match exactly
4. Ensure RLS policies are set correctly

For more information, visit:
- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)
- [Supabase Storage RLS](https://supabase.com/docs/guides/storage/security/access-control)

