import api from './api';
import { Platform } from 'react-native';

const TOKEN_KEY = 'ruzivo_auth_token';

export const saveToken = (token) => {
  if (Platform.OS === 'web') {
    localStorage.setItem(TOKEN_KEY, token);
  }
};

export const getToken = () => {
  if (Platform.OS === 'web') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
};

export const removeToken = () => {
  if (Platform.OS === 'web') {
    localStorage.removeItem(TOKEN_KEY);
  }
};

export const register = async (username, email, password) => {
  const res = await api.post('/auth/register', { username, email, password });
  saveToken(res.data.access_token);
  if (Platform.OS === 'web') window.location.reload();
  return res.data;
};

export const login = async (username, password) => {
  const form = new URLSearchParams();
  form.append('username', username);
  form.append('password', password);
  const res = await api.post('/auth/login', form.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  saveToken(res.data.access_token);
  if (Platform.OS === 'web') window.location.reload();
  return res.data;
};

export const logout = () => {
  removeToken();
  if (Platform.OS === 'web') window.location.reload();
};
