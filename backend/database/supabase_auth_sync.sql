-- Supabase Database Trigger to Sync Auth Users with Custom Users Table
-- This trigger automatically creates a user record in the 'users' table
-- when a new user signs up via Supabase Auth

-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (
    id,
    email,
    phone,
    full_name,
    role,
    status,
    language,
    is_kyc_verified,
    avatar_url,
    created_at,
    updated_at
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'phone', NULL),
    COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
    'customer',
    CASE 
      WHEN NEW.email_confirmed_at IS NOT NULL THEN 'active'
      ELSE 'pending_verification'
    END,
    COALESCE(NEW.raw_user_meta_data->>'language', 'en'),
    FALSE,
    NEW.raw_user_meta_data->>'avatar_url',
    NOW(),
    NOW()
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    updated_at = NOW();
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to call the function when a new user is created in auth.users
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to handle user updates
CREATE OR REPLACE FUNCTION public.handle_user_update()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE public.users
  SET
    email = NEW.email,
    phone = COALESCE(NEW.raw_user_meta_data->>'phone', users.phone),
    full_name = COALESCE(NEW.raw_user_meta_data->>'full_name', users.full_name),
    avatar_url = COALESCE(NEW.raw_user_meta_data->>'avatar_url', users.avatar_url),
    status = CASE 
      WHEN NEW.email_confirmed_at IS NOT NULL AND users.status = 'pending_verification' THEN 'active'
      ELSE users.status
    END,
    updated_at = NOW()
  WHERE id = NEW.id;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to call the function when a user is updated in auth.users
CREATE OR REPLACE TRIGGER on_auth_user_updated
  AFTER UPDATE ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_user_update();

-- Function to handle user deletion
CREATE OR REPLACE FUNCTION public.handle_user_delete()
RETURNS TRIGGER AS $$
BEGIN
  -- Soft delete: mark user as inactive instead of deleting
  UPDATE public.users
  SET
    status = 'inactive',
    updated_at = NOW()
  WHERE id = OLD.id;
  
  RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to call the function when a user is deleted in auth.users
CREATE OR REPLACE TRIGGER on_auth_user_deleted
  AFTER DELETE ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_user_delete();


