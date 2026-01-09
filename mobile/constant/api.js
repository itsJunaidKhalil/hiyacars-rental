// API Configuration
// For Android emulator, use: http://10.0.2.2:8000
// For iOS simulator, use: http://localhost:8000
// For physical device, use your computer's local IP: http://192.168.1.XXX:8000

import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Get API URL from environment variables
// Priority: 1. EXPO_PUBLIC_API_URL, 2. Platform-specific defaults
const getApiBaseUrl = () => {
  // Check if EXPO_PUBLIC_API_URL is set (works for both dev and production)
  // Try process.env first (more reliable), then Constants
  let envApiUrl = process.env.EXPO_PUBLIC_API_URL || 
                  Constants.expoConfig?.extra?.EXPO_PUBLIC_API_URL;
  
  // Skip if it's a template string (not interpolated)
  if (envApiUrl && envApiUrl.includes('${')) {
    envApiUrl = null;
  }
  
  if (envApiUrl) {
    // If environment variable is set, use it
    // For local development on Android emulator, replace localhost
    if (__DEV__ && Platform.OS === 'android' && envApiUrl.includes('localhost')) {
      return envApiUrl.replace('localhost', '10.0.2.2');
    }
    return envApiUrl;
  }
  
  // Fallback to platform-specific defaults (for backward compatibility)
  if (__DEV__) {
    // Development mode
    if (Platform.OS === 'android') {
      // Android emulator uses 10.0.2.2 to access localhost
      return 'http://10.0.2.2:8000';
    } else if (Platform.OS === 'ios') {
      // iOS simulator can use localhost
      return 'http://localhost:8000';
    } else {
      // Web or other platforms
      return 'http://localhost:8000';
    }
  } else {
    // Production mode - this should be set via EAS secrets
    console.warn('⚠️ EXPO_PUBLIC_API_URL not set! Please configure environment variables.');
    return 'https://your-production-api.com';
  }
};

export const API_BASE_URL = getApiBaseUrl();

// Debug: Log the API URL being used
console.log('🔗 API_BASE_URL:', API_BASE_URL);
console.log('📱 Platform:', Platform.OS);
console.log('🔧 ENV from Constants:', Constants.expoConfig?.extra?.EXPO_PUBLIC_API_URL);
console.log('🔧 ENV from process:', process.env.EXPO_PUBLIC_API_URL);

export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    REGISTER: `${API_BASE_URL}/api/v1/auth/register`,
    LOGIN: `${API_BASE_URL}/api/v1/auth/login`,
    ME: `${API_BASE_URL}/api/v1/auth/me`,
    REFRESH: `${API_BASE_URL}/api/v1/auth/refresh`,
    GOOGLE: `${API_BASE_URL}/api/v1/auth/google`,
    FACEBOOK: `${API_BASE_URL}/api/v1/auth/facebook`,
  },
  
  // Vehicle endpoints
  VEHICLES: {
    LIST: `${API_BASE_URL}/api/v1/vehicles/`,
    SEARCH: `${API_BASE_URL}/api/v1/vehicles/search`,
    DETAILS: (id) => `${API_BASE_URL}/api/v1/vehicles/${id}`,
    AVAILABILITY: (id) => `${API_BASE_URL}/api/v1/vehicles/${id}/availability`,
  },
  
  // Booking endpoints
  BOOKINGS: {
    CREATE: `${API_BASE_URL}/api/v1/bookings/`,
    LIST: `${API_BASE_URL}/api/v1/bookings/`,
    DETAILS: (id) => `${API_BASE_URL}/api/v1/bookings/${id}`,
    CANCEL: (id) => `${API_BASE_URL}/api/v1/bookings/${id}/cancel`,
  },
  
  // Payment endpoints
  PAYMENTS: {
    INTENT: `${API_BASE_URL}/api/v1/payments/intent`,
    DETAILS: (id) => `${API_BASE_URL}/api/v1/payments/${id}`,
    BOOKING_PAYMENT: (bookingId) => `${API_BASE_URL}/api/v1/payments/booking/${bookingId}`,
  },
  
  // KYC endpoints
  KYC: {
    CREATE: `${API_BASE_URL}/api/v1/kyc/`,
    GET: `${API_BASE_URL}/api/v1/kyc/`,
    UPLOAD_DOCUMENT: (type) => `${API_BASE_URL}/api/v1/kyc/documents/${type}`,
    UPLOAD_SIGNATURE: `${API_BASE_URL}/api/v1/kyc/signature`,
  },
  
  // Contract endpoints
  CONTRACTS: {
    CREATE: `${API_BASE_URL}/api/v1/contracts/`,
    GET: (id) => `${API_BASE_URL}/api/v1/contracts/${id}`,
    SIGN: (id) => `${API_BASE_URL}/api/v1/contracts/${id}/sign`,
    BOOKING_CONTRACT: (bookingId) => `${API_BASE_URL}/api/v1/contracts/booking/${bookingId}`,
  },
  
  // Loyalty endpoints
  LOYALTY: {
    POINTS: `${API_BASE_URL}/api/v1/loyalty/points`,
    TRANSACTIONS: `${API_BASE_URL}/api/v1/loyalty/transactions`,
    EARN: `${API_BASE_URL}/api/v1/loyalty/earn`,
    REDEEM: `${API_BASE_URL}/api/v1/loyalty/redeem`,
  },
  
  // Review endpoints
  REVIEWS: {
    CREATE: `${API_BASE_URL}/api/v1/reviews/`,
    VEHICLE_REVIEWS: (vehicleId) => `${API_BASE_URL}/api/v1/reviews/vehicle/${vehicleId}`,
    UPDATE: (id) => `${API_BASE_URL}/api/v1/reviews/${id}`,
    DELETE: (id) => `${API_BASE_URL}/api/v1/reviews/${id}`,
  },
};


