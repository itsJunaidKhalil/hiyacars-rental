# Supabase Database Schema SQL
# Run this in your Supabase SQL editor to create the tables

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'org_admin', 'agency_admin', 'staff', 'investor', 'support')),
    status TEXT NOT NULL DEFAULT 'pending_verification' CHECK (status IN ('active', 'inactive', 'suspended', 'pending_verification')),
    avatar_url TEXT,
    language TEXT DEFAULT 'en' CHECK (language IN ('en', 'ar')),
    is_kyc_verified BOOLEAN DEFAULT FALSE,
    organization_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('agency', 'rental_company')),
    email TEXT,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('sedan', 'hatchback', 'suv', 'luxury', 'sports', 'electric')),
    seats INTEGER NOT NULL,
    transmission TEXT NOT NULL CHECK (transmission IN ('manual', 'automatic')),
    fuel_type TEXT NOT NULL CHECK (fuel_type IN ('petrol', 'diesel', 'electric', 'hybrid')),
    color TEXT NOT NULL,
    license_plate TEXT NOT NULL UNIQUE,
    vin TEXT,
    status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'rented', 'maintenance', 'unavailable')),
    price_per_day DECIMAL(10, 2) NOT NULL,
    price_per_week DECIMAL(10, 2) NOT NULL,
    price_per_month DECIMAL(10, 2) NOT NULL,
    price_per_hour DECIMAL(10, 2),
    location TEXT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    images TEXT[] DEFAULT '{}',
    features TEXT[] DEFAULT '{}',
    organization_id UUID NOT NULL REFERENCES organizations(id),
    investor_id UUID,
    description TEXT,
    rating DECIMAL(3, 2) DEFAULT 0.0,
    total_reviews INTEGER DEFAULT 0,
    total_bookings INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES users(id),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    pickup_date TIMESTAMPTZ NOT NULL,
    return_date TIMESTAMPTZ NOT NULL,
    rental_type TEXT NOT NULL CHECK (rental_type IN ('hour', 'day', 'weekly', 'monthly')),
    pickup_location TEXT NOT NULL,
    return_location TEXT,
    base_price DECIMAL(10, 2) NOT NULL,
    surge_multiplier DECIMAL(3, 2) DEFAULT 1.0,
    driver_fee DECIMAL(10, 2) DEFAULT 0.0,
    platform_fee DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'rejected')),
    with_driver BOOLEAN DEFAULT FALSE,
    driver_id UUID,
    customer_gender TEXT CHECK (customer_gender IN ('Male', 'Female', 'Others')),
    special_requests TEXT,
    contract_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id),
    customer_id UUID NOT NULL REFERENCES users(id),
    amount DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'AED',
    method TEXT NOT NULL CHECK (method IN ('stripe_card', 'wallet', 'loyalty_points', 'mixed')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'refunded', 'partially_refunded')),
    stripe_payment_intent_id TEXT,
    stripe_charge_id TEXT,
    wallet_amount DECIMAL(10, 2) DEFAULT 0.0,
    loyalty_points_used INTEGER DEFAULT 0,
    description TEXT,
    failure_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- KYC table
CREATE TABLE IF NOT EXISTS kyc (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) UNIQUE,
    emirates_id_front TEXT,
    emirates_id_back TEXT,
    passport_front TEXT,
    passport_back TEXT,
    driving_license_front TEXT,
    driving_license_back TEXT,
    visa TEXT,
    signature_image TEXT,
    full_name TEXT NOT NULL,
    date_of_birth TIMESTAMPTZ,
    nationality TEXT,
    emirates_id_number TEXT,
    passport_number TEXT,
    driving_license_number TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'under_review', 'approved', 'rejected')),
    rejection_reason TEXT,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contracts table
CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) UNIQUE,
    customer_id UUID NOT NULL REFERENCES users(id),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    contract_number TEXT NOT NULL UNIQUE,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    rta_contract_id TEXT,
    rta_submission_status TEXT,
    rta_submission_date TIMESTAMPTZ,
    rta_response JSONB,
    pdf_url TEXT,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_rta', 'submitted_to_rta', 'rta_approved', 'rta_rejected', 'signed', 'active', 'completed', 'cancelled')),
    customer_signature_url TEXT,
    agency_signature_url TEXT,
    customer_signed_at TIMESTAMPTZ,
    agency_signed_at TIMESTAMPTZ,
    terms_and_conditions TEXT,
    special_conditions TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Loyalty Points table
CREATE TABLE IF NOT EXISTS loyalty_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) UNIQUE,
    total_points INTEGER DEFAULT 0,
    available_points INTEGER DEFAULT 0,
    lifetime_points INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Loyalty Transactions table
CREATE TABLE IF NOT EXISTS loyalty_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    booking_id UUID REFERENCES bookings(id),
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('earned', 'redeemed', 'expired', 'adjustment')),
    points INTEGER NOT NULL,
    description TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) UNIQUE,
    customer_id UUID NOT NULL REFERENCES users(id),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    rating DECIMAL(3, 2) NOT NULL CHECK (rating >= 1.0 AND rating <= 5.0),
    comment TEXT,
    cleanliness_rating DECIMAL(3, 2),
    comfort_rating DECIMAL(3, 2),
    value_rating DECIMAL(3, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Trail table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id UUID,
    details JSONB,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_organization ON vehicles(organization_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE INDEX IF NOT EXISTS idx_vehicles_category ON vehicles(category);
CREATE INDEX IF NOT EXISTS idx_bookings_customer ON bookings(customer_id);
CREATE INDEX IF NOT EXISTS idx_bookings_vehicle ON bookings(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_dates ON bookings(pickup_date, return_date);
CREATE INDEX IF NOT EXISTS idx_payments_booking ON payments(booking_id);
CREATE INDEX IF NOT EXISTS idx_payments_customer ON payments(customer_id);
CREATE INDEX IF NOT EXISTS idx_kyc_user ON kyc(user_id);
CREATE INDEX IF NOT EXISTS idx_contracts_booking ON contracts(booking_id);
CREATE INDEX IF NOT EXISTS idx_loyalty_user ON loyalty_points(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_vehicle ON reviews(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id);



