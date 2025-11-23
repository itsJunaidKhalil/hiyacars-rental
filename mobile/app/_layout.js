import { Stack } from "expo-router";
import { AuthProvider } from "../contexts/AuthContext";

export default () => {
  return (
    <AuthProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="(Authentication)" />
        <Stack.Screen name="Home" />
        <Stack.Screen name="auth/callback" />
      </Stack>
    </AuthProvider>
  );
};
