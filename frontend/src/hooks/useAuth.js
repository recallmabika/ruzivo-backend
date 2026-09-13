import { useState, useEffect, useCallback } from 'react';
import { getToken, saveToken, removeToken } from '../utils/storage';
import { login, register } from '../services/auth';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await getToken();
      console.log('checkAuth token:', token);
      setIsAuthenticated(!!token);
    } catch {
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = useCallback(async (username, password) => {
    const result = await login(username, password);
    console.log('login result:', result);
    const token = await getToken();
    console.log('token after login:', token);
    setIsAuthenticated(true);
    console.log('setIsAuthenticated called with true');
  }, []);

  const handleRegister = useCallback(async (username, email, password) => {
    await register(username, email, password);
    setIsAuthenticated(true);
  }, []);

  const handleLogout = useCallback(async () => {
    await removeToken();
    setIsAuthenticated(false);
  }, []);

  return { isAuthenticated, loading, handleLogin, handleRegister, handleLogout };
};
