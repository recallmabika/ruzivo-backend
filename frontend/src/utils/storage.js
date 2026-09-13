import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'ruzivo_auth_token';

export const saveToken = async (token) => {
  if (Platform.OS === 'web') return localStorage.setItem(TOKEN_KEY, token);
  return SecureStore.setItemAsync(TOKEN_KEY, token);
};

export const getToken = async () => {
  if (Platform.OS === 'web') return localStorage.getItem(TOKEN_KEY);
  return SecureStore.getItemAsync(TOKEN_KEY);
};

export const removeToken = async () => {
  if (Platform.OS === 'web') return localStorage.removeItem(TOKEN_KEY);
  return SecureStore.deleteItemAsync(TOKEN_KEY);
};
