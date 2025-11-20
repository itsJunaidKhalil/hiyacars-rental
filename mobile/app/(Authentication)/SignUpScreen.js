import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Image,
    TouchableOpacity,
    ScrollView,
    TextInput,
    Alert,
} from 'react-native';
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from '@expo/vector-icons';
import { router } from "expo-router";
// Assuming you have a component structure for standard inputs
import EmailInput from '../../components/EmailInput';
import PasswordInput from '../../components/PasswordInput';
import CustomButton from '../../components/CustomButton';
import Colors from '../../constant/Colors';
import CustomeFonts from '../../constant/customeFonts';
import { useAuth } from '../../contexts/AuthContext';

// Since the Country field is a standard text input without custom styling needed, 
// we will define a simple reusable component for it here, similar to the existing inputs.
const BasicTextInput = ({ value, onChangeText, placeholder = "Input" }) => (
    <View style={basicInputStyles.container}>
        <TextInput
            style={basicInputStyles.input}
            placeholder={placeholder}
            placeholderTextColor={Colors.TextSecondary}
            value={value}
            onChangeText={onChangeText}
            autoCapitalize="words"
            autoCorrect={false}
        />
    </View>
);

const basicInputStyles = StyleSheet.create({
    container: {
        width: '100%',
        marginBottom: 16,
    },
    input: {
        backgroundColor: Colors.White,
        borderRadius: 12,
        padding: 16,
        fontSize: 16,
        borderWidth: 1,
        borderColor: Colors.Border,
        color: Colors.TextPrimary,
        fontFamily: CustomeFonts.Lato_Regular,
    },
});


const SignUpScreen = () => {
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [phone, setPhone] = useState('');
    const [loading, setLoading] = useState(false);
    const { register, signInWithGoogle, signInWithFacebook } = useAuth();

    // Simple email validation
    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const handleSignUp = async () => {
        // Trim whitespace from inputs
        const trimmedEmail = email.trim();
        const trimmedFullName = fullName.trim();

        if (!trimmedFullName || !trimmedEmail || !password) {
            Alert.alert('Error', 'Please fill in all required fields');
            return;
        }

        // Validate email format
        if (!validateEmail(trimmedEmail)) {
            Alert.alert('Invalid Email', 'Please enter a valid email address (e.g., example@email.com)');
            return;
        }

        if (password.length < 6) {
            Alert.alert('Error', 'Password must be at least 6 characters');
            return;
        }

        setLoading(true);
        try {
            await register({
                email: trimmedEmail,
                password,
                full_name: trimmedFullName,
                phone: phone?.trim() || undefined,
                language: 'en',
            });
            Alert.alert('Success', 'Registration successful! Please check your email to confirm your account.', [
                { text: 'OK', onPress: () => router.back() }
            ]);
        } catch (error) {
            // Better error handling with detailed logging
            console.error('Sign up error:', error);
            console.error('Error message:', error.message);
            console.error('Error code:', error.status || error.code);
            
            let errorMessage = 'Failed to create account';
            if (error.message) {
                if (error.message.includes('already registered') || error.message.includes('already exists')) {
                    errorMessage = 'This email is already registered. Please login instead.';
                } else if (error.message.includes('invalid') || error.message.includes('Invalid')) {
                    errorMessage = 'Invalid email format. Please check your email address.';
                } else if (error.message.includes('password') || error.message.includes('Password')) {
                    errorMessage = 'Password is too weak. Please use a stronger password (at least 6 characters).';
                } else if (error.message.includes('Supabase URL')) {
                    errorMessage = 'Configuration error: Supabase is not properly configured. Please check your .env file.';
                } else if (error.message.includes('network') || error.message.includes('Network')) {
                    errorMessage = 'Network error: Please check your internet connection and try again.';
                } else {
                    errorMessage = error.message || 'Failed to create account. Please try again.';
                }
            }
            
            // Show detailed error in development
            if (__DEV__) {
                console.log('Full error object:', JSON.stringify(error, null, 2));
            }
            
            Alert.alert('Registration Failed', errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleLogin = () => {
        router.back(); // Go back to LoginScreen
    };

    const handleAppleLogin = async () => {
        // Apple OAuth can be added similarly
        Alert.alert('Coming Soon', 'Apple login will be available soon');
    };

    const handleGoogleLogin = async () => {
        try {
            setLoading(true);
            console.log('Starting Google login...');
            await signInWithGoogle();
            // Navigation is handled in AuthContext after successful OAuth
        } catch (error) {
            console.error('Google login error:', error);
            let errorMessage = 'Google login failed';
            if (error.message) {
                if (error.message.includes('cancelled')) {
                    errorMessage = 'Google login was cancelled';
                } else if (error.message.includes('network')) {
                    errorMessage = 'Network error. Please check your internet connection.';
                } else {
                    errorMessage = error.message;
                }
            }
            Alert.alert('Error', errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContent}>
                {/* Logo Section (Matches LoginScreen layout) */}
                <View style={styles.logoContainer}>
                    <Image
                        source={require('../../assets/icons/car_icon_main.png')}
                        style={styles.logo}
                        resizeMode="contain"
                    />
                </View>

                {/* Header Title */}
                <View style={styles.headerContainer}>
                    <Text style={styles.title}>Sign Up</Text>
                </View>

                {/* Input Fields */}
                <View style={styles.inputSection}>
                    <BasicTextInput
                        value={fullName}
                        onChangeText={setFullName}
                        placeholder="Full Name"
                    />
                    <EmailInput
                        value={email}
                        onChangeText={setEmail}
                        placeholder="Email Address"
                    />
                    <PasswordInput
                        value={password}
                        onChangeText={setPassword}
                        placeholder="Password"
                    />
                    <BasicTextInput
                        value={phone}
                        onChangeText={setPhone}
                        placeholder="Phone (optional)"
                        keyboardType="phone-pad"
                    />
                </View>

                {/* Main Action Buttons */}
                <CustomButton
                    title={loading ? "Signing up..." : "Sign up"}
                    onPress={handleSignUp}
                    variant="filled"
                    style={{ backgroundColor: Colors.Primary }}
                    disabled={loading}
                />

                <CustomButton
                    title="Login"
                    onPress={handleLogin}
                    variant="white"
                />

                {/* Divider */}
                <View style={styles.dividerContainer}>
                    <View style={styles.divider} />
                    <Text style={styles.dividerText}>Or</Text>
                    <View style={styles.divider} />
                </View>

                {/* Social Login Buttons */}
                <TouchableOpacity style={styles.socialButton} onPress={handleAppleLogin}>
                    <Ionicons name="logo-apple" size={24} color={Colors.TextPrimary} />
                    <Text style={styles.socialButtonText}>Apple</Text>
                </TouchableOpacity>

                <TouchableOpacity style={styles.socialButton} onPress={handleGoogleLogin}>
                    <Ionicons name="logo-google" size={24} color={Colors.TextPrimary} />
                    <Text style={styles.socialButtonText}>Google</Text>
                </TouchableOpacity>

                {/* Login Link */}
                <View style={styles.loginLinkContainer}>
                    <Text style={styles.loginLinkText}>Already have an account? </Text>
                    <TouchableOpacity onPress={handleLogin}>
                        <Text style={styles.loginLink}>Login.</Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.White,
    },
    scrollContent: {
        flexGrow: 1,
        paddingHorizontal: 24
    },
    logoContainer: {
        // --- FIX: Back to top-left alignment ---
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'flex-start',
        marginBottom: 0,
        marginTop: 0, // Removed extra top margin
    },
    logo: {
        // --- FIX: Small, white icon inside the dark circle ---
        width: 100,
        height: 100,
    },
    appName: {
        fontSize: 18,
        fontFamily: CustomeFonts.Lato_Bold,
        color: Colors.TextPrimary,
    },
    // --- Header Title ---
    headerContainer: {
        marginBottom: 40,
        alignItems: 'center',
    },
    title: {
        fontSize: 32,
        fontFamily: CustomeFonts.Gilroy_ExtraBold,
        color: Colors.TextPrimary,
    },
    inputSection: {
        marginBottom: 16,
    },
    // --- Divider Styles (Copied from LoginScreen) ---
    dividerContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginVertical: 24,
    },
    divider: {
        flex: 1,
        height: 1,
        backgroundColor: Colors.Border,
    },
    dividerText: {
        marginHorizontal: 16,
        fontSize: 14,
        color: Colors.TextSecondary,
        fontFamily: CustomeFonts.Lato_Regular,
    },
    // --- Social Button Styles (Copied from LoginScreen) ---
    socialButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: Colors.BackgroundLight,
        borderRadius: 12,
        paddingVertical: 16,
        marginBottom: 12,
        borderWidth: 1,
        borderColor: Colors.Border,
    },
    socialButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: Colors.TextPrimary,
        marginLeft: 12,
        fontFamily: CustomeFonts.Lato_Bold,
    },
    // --- Login Link (Copied and renamed from SignUp Link on LoginScreen) ---
    loginLinkContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 16,
        marginBottom: 24,
    },
    loginLinkText: {
        fontSize: 14,
        color: Colors.TextSecondary,
        fontFamily: CustomeFonts.Lato_Regular,
    },
    loginLink: {
        fontSize: 14,
        color: Colors.Primary,
        fontWeight: '600',
        fontFamily: CustomeFonts.Lato_Bold,
    },
});

export default SignUpScreen;
