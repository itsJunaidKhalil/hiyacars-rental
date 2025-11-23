import { useEffect } from 'react';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { supabase } from '../../services/supabase';
import * as Linking from 'expo-linking';

export default function AuthCallback() {
  const router = useRouter();
  const params = useLocalSearchParams();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        console.log('Auth callback handler received');
        console.log('Params:', params);

        // Get the initial URL if available (from deep link)
        const initialUrl = await Linking.getInitialURL();
        console.log('Initial URL:', initialUrl);

        // Also listen for URL changes (in case the callback comes after component mounts)
        const subscription = Linking.addEventListener('url', async (event) => {
          console.log('URL event received:', event.url);
          await processCallbackUrl(event.url);
        });

        // Process initial URL if available
        if (initialUrl) {
          await processCallbackUrl(initialUrl);
        } else {
          // Wait a bit for Supabase to process the URL and set the session
          await new Promise(resolve => setTimeout(resolve, 2000));
          await checkSession();
        }

        return () => {
          subscription?.remove();
        };
      } catch (error) {
        console.error('Auth callback error:', error);
        router.replace('/(Authentication)/LoginScreen');
      }
    };

    const processCallbackUrl = async (url) => {
      try {
        console.log('Processing callback URL:', url);
        
        // Extract tokens from URL
        let access_token = null;
        let refresh_token = null;
        
        if (url.includes('#')) {
          const hash = url.split('#')[1];
          const hashParams = new URLSearchParams(hash);
          access_token = hashParams.get('access_token');
          refresh_token = hashParams.get('refresh_token');
        }
        
        if (url.includes('?')) {
          const query = url.split('?')[1].split('#')[0];
          const queryParams = new URLSearchParams(query);
          if (!access_token) access_token = queryParams.get('access_token');
          if (!refresh_token) refresh_token = queryParams.get('refresh_token');
        }
        
        if (access_token && refresh_token) {
          console.log('Tokens found, setting session...');
          const { data: sessionData, error: sessionError } = await supabase.auth.setSession({
            access_token,
            refresh_token,
          });
          
          if (sessionError) {
            console.error('Error setting session:', sessionError);
            throw sessionError;
          }
          
          if (sessionData.session) {
            console.log('Session created successfully in callback handler');
            router.replace('/(tabs)/HomeScreen');
            return;
          }
        }
        
        // If no tokens, wait and check session
        await new Promise(resolve => setTimeout(resolve, 1500));
        await checkSession();
      } catch (error) {
        console.error('Error processing callback URL:', error);
        await checkSession();
      }
    };

    const checkSession = async () => {
      try {
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError) {
          console.error('Error getting session:', sessionError);
          router.replace('/(Authentication)/LoginScreen');
          return;
        }

        if (session) {
          console.log('Session found in callback handler, user:', session.user?.email);
          router.replace('/(tabs)/HomeScreen');
        } else {
          console.log('No session found after callback');
          console.log('Possible reasons:');
          console.log('1. OAuth callback failed');
          console.log('2. Redirect URL not properly configured in Supabase');
          console.log('3. Tokens not in expected format');
          router.replace('/(Authentication)/LoginScreen');
        }
      } catch (error) {
        console.error('Error checking session:', error);
        router.replace('/(Authentication)/LoginScreen');
      }
    };

    handleAuthCallback();
  }, [params, router]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#0000ff" />
      <Text style={styles.text}>Completing authentication...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  text: {
    marginTop: 20,
    fontSize: 16,
    color: '#333',
  },
});
