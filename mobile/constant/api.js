// API Configuration
// For Android emulator, use: http://10.0.2.2:8000
// For iOS simulator, use: http://localhost:8000
// For physical device, use your computer's local IP: http://192.168.1.XXX:8000

import { Platform } from 'react-native';

// Determine the API base URL based on platform
const getApiBaseUrl = () => {
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
    // Production mode - update this with your production API URL
    return 'https://your-production-api.com';
  }
};

export const API_BASE_URL = getApiBaseUrl();

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


