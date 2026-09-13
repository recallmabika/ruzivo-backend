import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import ChatScreen from '../screens/ChatScreen';
import VoiceScreen from '../screens/VoiceScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const MainTabs = ({ onLogout }) => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ color, size }) => {
        const icons = { Chat: 'chatbubble', Voice: 'mic' };
        return <Ionicons name={icons[route.name]} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#2E7D32',
      tabBarInactiveTintColor: '#888',
      headerShown: false,
    })}
  >
    <Tab.Screen name="Chat" component={ChatScreen} options={{ title: 'Nhaurirano' }} />
    <Tab.Screen name="Voice" component={VoiceScreen} options={{ title: 'Inzwi' }} />
  </Tab.Navigator>
);

const AppNavigator = ({ isAuthenticated, onLogin, onRegister, onLogout }) => (
  <NavigationContainer>
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isAuthenticated ? (
        <>
          <Stack.Screen name="Login">
            {(props) => <LoginScreen {...props} onLogin={onLogin} />}
          </Stack.Screen>
          <Stack.Screen name="Register">
            {(props) => <RegisterScreen {...props} onRegister={onRegister} />}
          </Stack.Screen>
        </>
      ) : (
        <Stack.Screen name="Main">
          {(props) => <MainTabs {...props} onLogout={onLogout} />}
        </Stack.Screen>
      )}
    </Stack.Navigator>
  </NavigationContainer>
);

export default AppNavigator;
