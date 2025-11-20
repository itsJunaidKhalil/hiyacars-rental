import 'react-native-url-polyfill/auto'; // Required for Supabase in React Native
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// Get API base URL (same logic as api.js)
const getApiBaseUrl = () => {
  if (__DEV__) {
    if (Platform.OS === 'android') {
      return 'http://10.0.2.2:8000';
    } else if (Platform.OS === 'ios') {
      return 'http://localhost:8000';
    } else {
      return 'http://localhost:8000';
    }
  } else {
    return 'https://your-production-api.com';
  }
};

// Supabase configuration
// Get from environment variables or use defaults
// Make sure to set these in your .env file
const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL || 'YOUR_SUPABASE_URL';
const SUPABASE_ANON_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || 'YOUR_SUPABASE_ANON_KEY';

if (SUPABASE_URL === 'YOUR_SUPABASE_URL' || SUPABASE_ANON_KEY === 'YOUR_SUPABASE_ANON_KEY') {
  console.warn('⚠️ Supabase credentials not configured! Please set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY in your .env file');
}

// Create Supabase client with AsyncStorage for session persistence
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true, // Enable URL detection for OAuth callbacks
    flowType: 'pkce', // Use PKCE flow for better security (required for mobile)
  },
});

// Helper to get the API base URL
export const API_BASE_URL = getApiBaseUrl();

