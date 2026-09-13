import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { View, ActivityIndicator } from 'react-native';
import { useAuth } from './src/hooks/useAuth';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import MainApp from './src/navigation/MainApp';

export default function App() {
  const { isAuthenticated, loading, handleLogin, handleRegister, handleLogout } = useAuth();
  const [showRegister, setShowRegister] = React.useState(false);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#2E7D32" />
      </View>
    );
  }

  if (!isAuthenticated) {
    if (showRegister) {
      return (
        <>
          <StatusBar style="light" />
          <RegisterScreen
            onRegister={handleRegister}
            onNavigateLogin={() => setShowRegister(false)}
          />
        </>
      );
    }
    return (
      <>
        <StatusBar style="light" />
        <LoginScreen
          onLogin={handleLogin}
          onNavigateRegister={() => setShowRegister(true)}
        />
      </>
    );
  }

  return (
    <>
      <StatusBar style="light" />
      <MainApp onLogout={handleLogout} />
    </>
  );
}
