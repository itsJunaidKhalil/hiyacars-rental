import { API_BASE_URL, API_ENDPOINTS } from '../constant/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const TOKEN_KEY = '@auth_token';
const USER_KEY = '@user_data';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = null;
  }

  // Token management
  async setToken(token) {
    this.token = token;
    if (token) {
      await AsyncStorage.setItem(TOKEN_KEY, token);
    } else {
      await AsyncStorage.removeItem(TOKEN_KEY);
    }
  }

  async getToken() {
    // Try to get token from AsyncStorage first
    if (!this.token) {
      this.token = await AsyncStorage.getItem(TOKEN_KEY);
    }
    
    // If no token, try to get from Supabase session
    if (!this.token) {
      try {
        const { supabase } = await import('./supabase');
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.access_token) {
          this.token = session.access_token;
          await this.setToken(session.access_token);
        }
      } catch (error) {
        console.log('Could not get Supabase session:', error);
      }
    }
    
    return this.token;
  }

  async clearToken() {
    this.token = null;
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(USER_KEY);
  }

  // User data management
  async setUser(user) {
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  async getUser() {
    const userData = await AsyncStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const token = await this.getToken();
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(endpoint, {
        ...options,
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
      });

      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      let data;
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        const error = data.detail || data.message || 'Request failed';
        throw new Error(error);
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Note: Register is now handled by Supabase Auth in AuthContext
  // This method is kept for backward compatibility but should use Supabase Auth
  async register(userData) {
    // This should not be called directly - use AuthContext.register instead
    throw new Error('Use AuthContext.register() instead of ApiService.register()');
  }

  // Note: Login is now handled by Supabase Auth in AuthContext
  // This method is kept for backward compatibility but should use Supabase Auth
  async login(email, password) {
    // This should not be called directly - use AuthContext.login instead
    throw new Error('Use AuthContext.login() instead of ApiService.login()');
  }

  async getMe() {
    const response = await this.request(API_ENDPOINTS.AUTH.ME, {
      method: 'GET',
    });
    await this.setUser(response);
    return response;
  }

  async updateProfile(userData) {
    const response = await this.request(API_ENDPOINTS.AUTH.ME, {
      method: 'PUT',
      body: userData,
    });
    await this.setUser(response);
    return response;
  }

  async logout() {
    await this.clearToken();
  }

  // Vehicle methods
  async getVehicles(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString 
      ? `${API_ENDPOINTS.VEHICLES.LIST}?${queryString}`
      : API_ENDPOINTS.VEHICLES.LIST;
    
    return this.request(url, {
      method: 'GET',
    });
  }

  async searchVehicles(searchParams) {
    const queryString = new URLSearchParams(searchParams).toString();
    return this.request(`${API_ENDPOINTS.VEHICLES.SEARCH}?${queryString}`, {
      method: 'GET',
    });
  }

  async getVehicle(id) {
    return this.request(API_ENDPOINTS.VEHICLES.DETAILS(id), {
      method: 'GET',
    });
  }

  async checkAvailability(vehicleId, startDate, endDate) {
    const queryString = new URLSearchParams({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
    }).toString();
    
    return this.request(`${API_ENDPOINTS.VEHICLES.AVAILABILITY(vehicleId)}?${queryString}`, {
      method: 'GET',
    });
  }

  // Booking methods
  async createBooking(bookingData) {
    return this.request(API_ENDPOINTS.BOOKINGS.CREATE, {
      method: 'POST',
      body: {
        ...bookingData,
        pickup_date: bookingData.pickup_date.toISOString(),
        return_date: bookingData.return_date.toISOString(),
      },
    });
  }

  async getBookings(status = null) {
    const queryString = status ? `?status_filter=${status}` : '';
    return this.request(`${API_ENDPOINTS.BOOKINGS.LIST}${queryString}`, {
      method: 'GET',
    });
  }

  async getBooking(id) {
    return this.request(API_ENDPOINTS.BOOKINGS.DETAILS(id), {
      method: 'GET',
    });
  }

  async cancelBooking(id) {
    return this.request(API_ENDPOINTS.BOOKINGS.CANCEL(id), {
      method: 'POST',
    });
  }

  // Payment methods
  async createPaymentIntent(paymentData) {
    return this.request(API_ENDPOINTS.PAYMENTS.INTENT, {
      method: 'POST',
      body: paymentData,
    });
  }

  // KYC methods
  async createKYC(kycData) {
    return this.request(API_ENDPOINTS.KYC.CREATE, {
      method: 'POST',
      body: {
        ...kycData,
        date_of_birth: kycData.date_of_birth?.toISOString(),
      },
    });
  }

  async getKYC() {
    return this.request(API_ENDPOINTS.KYC.GET, {
      method: 'GET',
    });
  }

  async uploadKYCDocument(documentType, side, fileUri) {
    // For file upload, we'll use FormData
    const formData = new FormData();
    formData.append('file', {
      uri: fileUri,
      type: 'image/jpeg',
      name: 'document.jpg',
    });
    formData.append('side', side);

    const token = await this.getToken();
    
    const response = await fetch(`${API_ENDPOINTS.KYC.UPLOAD_DOCUMENT(documentType)}?side=${side}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  // Loyalty methods
  async getLoyaltyPoints() {
    return this.request(API_ENDPOINTS.LOYALTY.POINTS, {
      method: 'GET',
    });
  }

  async getLoyaltyTransactions() {
    return this.request(API_ENDPOINTS.LOYALTY.TRANSACTIONS, {
      method: 'GET',
    });
  }

  // Review methods
  async createReview(reviewData) {
    return this.request(API_ENDPOINTS.REVIEWS.CREATE, {
      method: 'POST',
      body: reviewData,
    });
  }

  async getVehicleReviews(vehicleId) {
    return this.request(API_ENDPOINTS.REVIEWS.VEHICLE_REVIEWS(vehicleId), {
      method: 'GET',
    });
  }
}

export default new ApiService();

