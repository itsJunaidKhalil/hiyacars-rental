import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Image,
    TouchableOpacity,
    ScrollView,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from '@expo/vector-icons';
import { router } from "expo-router";
import EmailInput from '../../components/EmailInput';
import PasswordInput from '../../components/PasswordInput';
import CustomButton from '../../components/CustomButton';
import Colors from '../../constant/Colors'; // Importing Colors
import CustomeFonts from '../../constant/customeFonts'; // Importing Custom Fonts for text styling
import { useAuth } from '../../contexts/AuthContext';

const LoginScreen = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(true);
    const [loading, setLoading] = useState(false);
    const { login, signInWithGoogle, signInWithFacebook } = useAuth();

    // Simple email validation
    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const handleLogin = async () => {
        const trimmedEmail = email.trim();
        
        if (!trimmedEmail || !password) {
            Alert.alert('Error', 'Please fill in all fields');
            return;
        }

        // Validate email format
        if (!validateEmail(trimmedEmail)) {
            Alert.alert('Invalid Email', 'Please enter a valid email address (e.g., example@email.com)');
            return;
        }

        setLoading(true);
        try {
            await login(trimmedEmail, password);
            router.replace('/(tabs)/HomeScreen'); // Navigate to HomeScreen after login
        } catch (error) {
            let errorMessage = 'Invalid email or password';
            if (error.message) {
                if (error.message.includes('Invalid login credentials')) {
                    errorMessage = 'Invalid email or password. Please try again.';
                } else if (error.message.includes('Email not confirmed')) {
                    errorMessage = 'Please check your email and confirm your account before logging in.';
                } else {
                    errorMessage = error.message;
                }
            }
            Alert.alert('Login Failed', errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleSignUp = () => {
        router.push('/SignUpScreen');
    };

    const handleForgotPassword = () => {
        router.push('/ForgotPasswordScreen');
    };

    const handleAppleLogin = async () => {
        // Apple OAuth can be added similarly
        Alert.alert('Coming Soon', 'Apple login will be available soon');
    };

    const handleGoogleLogin = async () => {
        try {
            setLoading(true);
            await signInWithGoogle();
            // OAuth will redirect, so navigation is handled by Supabase
        } catch (error) {
            Alert.alert('Error', error.message || 'Google login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContent}>
                {/* Logo Section - Now Top-Left Aligned with Text */}
                <View style={styles.logoContainer}>
                    <Image
                        source={require('../../assets/icons/car_icon_main.png')}
                        style={styles.logo}
                        resizeMode="contain"
                    />
                </View>

                {/* Welcome Text - Aligned to Left, removed unnecessary centering */}
                <View style={styles.welcomeContainer}>
                    <Text style={styles.welcomeTitle}>Welcome Back</Text>
                    <Text style={styles.welcomeSubtitle}>Ready to hit the road?</Text>
                </View>

                {/* Input Fields */}
                <View style={styles.inputContainer}>
                    <EmailInput
                        value={email}
                        onChangeText={setEmail}
                        placeholder="Email/Phone Number"
                    />

                    <PasswordInput
                        value={password}
                        onChangeText={setPassword}
                        placeholder="Password"
                    />
                </View>

                {/* Remember Me & Forgot Password */}
                <View style={styles.optionsContainer}>
                    <TouchableOpacity
                        style={styles.rememberMeContainer}
                        onPress={() => setRememberMe(!rememberMe)}
                    >
                        <View style={[styles.checkbox, rememberMe && styles.checkboxChecked]}>
                            {rememberMe && <Ionicons name="checkmark" size={18} color={Colors.White} />}
                        </View>
                        <Text style={styles.rememberMeText}>Remember Me</Text>
                    </TouchableOpacity>

                    <TouchableOpacity onPress={handleForgotPassword}>
                        <Text style={styles.forgotPasswordText}>Forgot Password</Text>
                    </TouchableOpacity>
                </View>

                {/* Login Button */}
                <CustomButton
                    title={loading ? "Logging in..." : "Login"}
                    onPress={handleLogin}
                    variant="filled"
                    style={{ backgroundColor: Colors.Primary }}
                    disabled={loading}
                />

                {/* Sign Up Button */}
                <CustomButton
                    title="Sign up"
                    onPress={handleSignUp}
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

                {/* Sign Up Link */}
                <View style={styles.signUpLinkContainer}>
                    <Text style={styles.signUpLinkText}>Don't have an account? </Text>
                    <TouchableOpacity onPress={handleSignUp}>
                        <Text style={styles.signUpLink}>Sign Up.</Text>
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
        paddingHorizontal: 24,
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
        fontFamily: CustomeFonts.Lato_Bold, // Added a font
        color: Colors.TextPrimary,
    },
    welcomeContainer: {
        marginBottom: 32,
        alignItems: 'flex-start', // Aligned to left
    },
    welcomeTitle: {
        fontSize: 32,
        fontFamily: CustomeFonts.Gilroy_ExtraBold, // Added a font
        color: Colors.TextPrimary,
        marginBottom: 4,
        textAlign: 'left',
    },
    welcomeSubtitle: {
        fontSize: 32,
        fontFamily: CustomeFonts.Gilroy_ExtraBold, // Added a font
        color: Colors.TextPrimary,
        textAlign: 'left',
    },
    inputContainer: {
        marginBottom: 16,
    },
    optionsContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 24,
    },
    rememberMeContainer: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    checkbox: {
        width: 24,
        height: 24,
        borderRadius: 6,
        borderWidth: 2,
        borderColor: Colors.Border,
        marginRight: 8,
        justifyContent: 'center',
        alignItems: 'center',
    },
    checkboxChecked: {
        backgroundColor: Colors.Primary,
        borderColor: Colors.Primary,
    },
    rememberMeText: {
        fontSize: 14,
        color: Colors.TextSecondary,
    },
    forgotPasswordText: {
        fontSize: 14,
        color: Colors.TextSecondary,
        fontWeight: '500',
        fontFamily: CustomeFonts.Lato_Regular, // Added a font
    },
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
        fontFamily: CustomeFonts.Lato_Regular, // Added a font
    },
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
        fontFamily: CustomeFonts.Lato_Bold, // Added a font
    },
    signUpLinkContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 16,
        marginBottom: 24,
    },
    signUpLinkText: {
        fontSize: 14,
        color: Colors.TextSecondary,
        fontFamily: CustomeFonts.Lato_Regular, // Added a font
    },
    signUpLink: {
        fontSize: 14,
        color: Colors.Primary,
        fontWeight: '600',
        fontFamily: CustomeFonts.Lato_Bold, // Added a font
    },
});

export default LoginScreen;
