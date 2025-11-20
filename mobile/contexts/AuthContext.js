import React, { createContext, useState, useContext, useEffect } from 'react';
import { supabase } from '../services/supabase';
import ApiService from '../services/api';
import { router } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';

// Complete the auth session for better OAuth handling
WebBrowser.maybeCompleteAuthSession();

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is already logged in on app start
  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session?.user) {
        setUser(session.user);
        setIsAuthenticated(true);
        // Sync user data with backend
        syncUserWithBackend(session.user);
      }
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setSession(session);
      if (session?.user) {
        setUser(session.user);
        setIsAuthenticated(true);
        // Sync user data with backend
        await syncUserWithBackend(session.user);
      } else {
        setUser(null);
        setIsAuthenticated(false);
        await ApiService.clearToken();
      }
      setLoading(false);
    });

    // Listen for deep links (OAuth callbacks)
    const handleDeepLink = async (event) => {
      const url = event.url;
      console.log('Deep link received in AuthContext:', url);
      
      // Check if it's an OAuth callback
      if (url && (url.includes('auth/callback') || url.includes('access_token'))) {
        console.log('Processing OAuth deep link...');
        
        // Extract tokens
        let access_token = null;
        let refresh_token = null;
        
        if (url.includes('#')) {
          const hash = url.split('#')[1];
          const hashParams = new URLSearchParams(hash);
          access_token = hashParams.get('access_token');
          refresh_token = hashParams.get('refresh_token');
        }
        
        if (url.includes('?') && (!access_token || !refresh_token)) {
          const query = url.split('?')[1].split('#')[0];
          const queryParams = new URLSearchParams(query);
          if (!access_token) access_token = queryParams.get('access_token');
          if (!refresh_token) refresh_token = queryParams.get('refresh_token');
        }
        
        if (access_token && refresh_token) {
          console.log('Tokens found in deep link, setting session...');
          try {
            const { data: sessionData, error: sessionError } = await supabase.auth.setSession({
              access_token,
              refresh_token,
            });
            
            if (sessionError) {
              console.error('Error setting session from deep link:', sessionError);
              return;
            }
            
            if (sessionData.session) {
              console.log('Session created from deep link');
              setSession(sessionData.session);
              setUser(sessionData.session.user);
              setIsAuthenticated(true);
              await syncUserWithBackend(sessionData.session.user);
              router.replace('/(tabs)/HomeScreen');
            }
          } catch (error) {
            console.error('Error processing deep link:', error);
          }
        }
      }
    };

    // Get initial URL
    Linking.getInitialURL().then((url) => {
      if (url) {
        handleDeepLink({ url });
      }
    });

    // Listen for URL changes
    const linkingSubscription = Linking.addEventListener('url', handleDeepLink);

    return () => {
      subscription.unsubscribe();
      linkingSubscription?.remove();
    };
  }, []);

  // Sync Supabase Auth user with backend users table
  const syncUserWithBackend = async (supabaseUser) => {
    try {
      console.log('Syncing user with backend:', supabaseUser.email);
      
      // Get Supabase JWT token
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        // Store Supabase token for backend API calls
        await ApiService.setToken(session.access_token);
        
        // Try to get user from backend, if not exists, create it
        try {
          const backendUser = await ApiService.getMe();
          console.log('Backend user found:', backendUser.email);
          // Update user data if needed
          if (backendUser) {
            setUser({ ...supabaseUser, ...backendUser });
          }
        } catch (error) {
          // User doesn't exist in backend, try to create it
          console.log('User not found in backend, attempting to create...');
          try {
            // The backend should create the user automatically via database trigger
            // But we can also try to call the backend API if needed
            // For now, just log - the database trigger should handle it
            console.log('User will be created via database trigger or backend API');
          } catch (createError) {
            console.error('Error creating user in backend:', createError);
            // Don't throw - user exists in Supabase Auth, which is the main thing
          }
        }
      } else {
        console.warn('No session access token available for backend sync');
      }
    } catch (error) {
      console.error('Error syncing user with backend:', error);
      // Don't throw - this is not critical for OAuth flow
    }
  };

  const register = async (userData) => {
    try {
      console.log('Registering user:', { email: userData.email, full_name: userData.full_name });
      
      // Validate Supabase connection
      const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
      if (!supabaseUrl || supabaseUrl === 'YOUR_SUPABASE_URL') {
        throw new Error('Supabase URL is not configured. Please check your .env file.');
      }

      // Create user in Supabase Auth
      const { data, error } = await supabase.auth.signUp({
        email: userData.email,
        password: userData.password,
        options: {
          data: {
            full_name: userData.full_name,
            phone: userData.phone,
            language: userData.language || 'en',
          },
          emailRedirectTo: 'car-rental://auth/callback',
        },
      });

      if (error) {
        console.error('Registration error:', error);
        console.error('Error details:', JSON.stringify(error, null, 2));
        throw error;
      }

      console.log('Registration response:', { 
        user: data.user?.id, 
        session: data.session ? 'present' : 'absent',
        emailConfirmed: data.user?.email_confirmed_at ? 'yes' : 'no'
      });

      // If email confirmation is disabled, user gets a session immediately
      // If email confirmation is enabled, user needs to confirm email first
      if (data.user && data.session) {
        // User is immediately signed in (email confirmation disabled)
        console.log('User registered and signed in immediately');
        setSession(data.session);
        setUser(data.user);
        setIsAuthenticated(true);
        await syncUserWithBackend(data.user);
        router.replace('/(tabs)/HomeScreen');
      } else if (data.user && !data.session) {
        // User created but needs to confirm email (email confirmation enabled)
        console.log('User registered, email confirmation required');
        // Don't navigate - let the signup screen show success message
        // User will need to confirm email before they can log in
      }

      return data;
    } catch (error) {
      console.error('Registration failed:', error);
      console.error('Error message:', error.message);
      console.error('Error code:', error.status || error.code);
      throw error;
    }
  };

  const login = async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      if (data.session) {
        setSession(data.session);
        setUser(data.user);
        setIsAuthenticated(true);
        await syncUserWithBackend(data.user);
        // Navigate to home after successful login
        router.replace('/(tabs)/HomeScreen');
      }

      return data;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      
      setUser(null);
      setSession(null);
      setIsAuthenticated(false);
      await ApiService.clearToken();
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  const resetPassword = async (email) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email);
      if (error) throw error;
      return true;
    } catch (error) {
      throw error;
    }
  };

  const updatePassword = async (newPassword) => {
    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      });
      if (error) throw error;
      return true;
    } catch (error) {
      throw error;
    }
  };

  // OAuth providers
  const signInWithGoogle = async () => {
    try {
      console.log('Starting Google OAuth...');
      
      // Get Supabase URL from environment
      const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
      if (!supabaseUrl) {
        throw new Error('Supabase URL is not configured');
      }

      // For mobile OAuth, we need to use the app's deep link scheme
      // But first, we must configure this in Supabase Dashboard as a redirect URL
      // The format should be: car-rental://auth/callback
      const redirectUrl = __DEV__ 
        ? `car-rental://auth/callback`  // Use deep link scheme
        : `car-rental://auth/callback`; // Same for production
      
      console.log('Using redirect URL:', redirectUrl);
      
      // Get the OAuth URL from Supabase
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          // Use the app's deep link scheme for redirect
          redirectTo: redirectUrl,
          // Skip browser redirect since we're handling it manually
          skipBrowserRedirect: true,
        },
      });

      if (error) {
        console.error('OAuth error:', error);
        throw error;
      }

      if (data?.url) {
        console.log('Opening OAuth URL:', data.url);
        
        // Open the OAuth URL in the browser
        // The redirect URL must match what's configured in Supabase
        const result = await WebBrowser.openAuthSessionAsync(
          data.url,
          redirectUrl  // Use the same redirect URL
        );

        console.log('OAuth result:', result);

        if (result.type === 'success') {
          // Extract the URL from the result
          const url = result.url;
          console.log('OAuth callback URL:', url);
          
          // Parse the URL to extract tokens
          const parsedUrl = Linking.parse(url);
          console.log('Parsed URL:', parsedUrl);
          
          // Extract tokens from URL hash or query params
          let access_token = null;
          let refresh_token = null;
          let error_description = null;
          
          // Check hash fragment (most common for OAuth)
          if (url.includes('#')) {
            const hash = url.split('#')[1];
            const hashParams = new URLSearchParams(hash);
            access_token = hashParams.get('access_token');
            refresh_token = hashParams.get('refresh_token');
            error_description = hashParams.get('error_description');
          }
          
          // Check query params as fallback
          if (!access_token && parsedUrl.queryParams) {
            access_token = parsedUrl.queryParams.access_token || parsedUrl.queryParams['#access_token'];
            refresh_token = parsedUrl.queryParams.refresh_token || parsedUrl.queryParams['#refresh_token'];
            error_description = parsedUrl.queryParams.error_description;
          }
          
          // If we have an error, throw it
          if (error_description) {
            console.error('OAuth error in callback:', error_description);
            throw new Error(error_description);
          }
          
          // If we have tokens, set the session
          if (access_token && refresh_token) {
            console.log('Tokens found in callback URL, setting session...');
            
            const { data: sessionData, error: sessionError } = await supabase.auth.setSession({
              access_token,
              refresh_token,
            });
            
            if (sessionError) {
              console.error('Error setting session:', sessionError);
              throw new Error(`Failed to set session: ${sessionError.message}`);
            }
            
            if (sessionData.session) {
              console.log('Session created successfully');
              setSession(sessionData.session);
              setUser(sessionData.session.user);
              setIsAuthenticated(true);
              await syncUserWithBackend(sessionData.session.user);
              router.replace('/(tabs)/HomeScreen');
            } else {
              throw new Error('Session data not returned after setting session');
            }
          } else {
            // If no tokens in URL, wait for Supabase to process it automatically
            console.log('No tokens in URL, waiting for Supabase to process...');
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Check if we have a session now
            const { data: { session }, error: sessionError } = await supabase.auth.getSession();
            
            if (sessionError) {
              console.error('Error getting session:', sessionError);
              throw new Error(`Failed to get session: ${sessionError.message}`);
            }
            
            if (session) {
              console.log('Session created successfully (auto-detected)');
              setSession(session);
              setUser(session.user);
              setIsAuthenticated(true);
              await syncUserWithBackend(session.user);
              router.replace('/(tabs)/HomeScreen');
            } else {
              console.error('No session found after OAuth callback');
              console.error('Callback URL was:', url);
              throw new Error('Failed to create session after OAuth. Please check console logs for details.');
            }
          }
        } else if (result.type === 'cancel') {
          console.log('OAuth cancelled by user');
          throw new Error('OAuth login was cancelled');
        } else {
          console.error('OAuth failed:', result);
          throw new Error('OAuth login failed');
        }
      } else {
        throw new Error('No OAuth URL returned from Supabase');
      }

      return data;
    } catch (error) {
      console.error('Google OAuth error:', error);
      throw error;
    }
  };

  const signInWithFacebook = async () => {
    try {
      console.log('Starting Facebook OAuth...');
      
      // Use the app's deep link scheme
      const redirectUrl = `car-rental://auth/callback`;
      
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'facebook',
        options: {
          redirectTo: redirectUrl,
          skipBrowserRedirect: true,
        },
      });

      if (error) {
        console.error('OAuth error:', error);
        throw error;
      }

      if (data?.url) {
        console.log('Opening OAuth URL:', data.url);
        
        const result = await WebBrowser.openAuthSessionAsync(
          data.url,
          redirectUrl
        );

        console.log('OAuth result:', result);

        if (result.type === 'success') {
          const url = result.url;
          console.log('OAuth callback URL:', url);
          
          // Supabase will automatically handle the session from the URL
          await new Promise(resolve => setTimeout(resolve, 1500));
          
          const { data: { session }, error: sessionError } = await supabase.auth.getSession();
          
          if (sessionError) {
            console.error('Error getting session:', sessionError);
            throw new Error('Failed to get session after OAuth');
          }
          
          if (session) {
            console.log('Session created successfully');
            setSession(session);
            setUser(session.user);
            setIsAuthenticated(true);
            await syncUserWithBackend(session.user);
            router.replace('/(tabs)/HomeScreen');
          } else {
            console.log('No session yet, navigating to callback handler...');
            router.replace('/auth/callback');
          }
        } else if (result.type === 'cancel') {
          console.log('OAuth cancelled by user');
          throw new Error('OAuth login was cancelled');
        } else {
          console.error('OAuth failed:', result);
          throw new Error('OAuth login failed');
        }
      } else {
        throw new Error('No OAuth URL returned from Supabase');
      }

      return data;
    } catch (error) {
      console.error('Facebook OAuth error:', error);
      throw error;
    }
  };

  const updateUser = (userData) => {
    setUser(userData);
  };

  const value = {
    user,
    session,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    resetPassword,
    updatePassword,
    signInWithGoogle,
    signInWithFacebook,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
