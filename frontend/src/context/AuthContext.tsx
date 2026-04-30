import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const register = async (username: string, email: string, password: string) => {
    const response = await fetch('/cv-ats/api/auth/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      // Handle specific error messages
      if (error.username) {
        throw new Error(error.username[0] || 'Registration failed');
      } else if (error.email) {
        throw new Error(error.email[0] || 'Registration failed');
      } else if (error.password) {
        throw new Error(error.password[0] || 'Registration failed');
      } else if (error.error) {
        throw new Error(error.error);
      } else {
        throw new Error('Registration failed. Please try again.');
      }
    }

    const data = await response.json();
    // Registration successful - tokens are returned automatically
    const { access, refresh, user: userData } = data;

    // Store tokens
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(userData));

    setToken(access);
    setUser(userData);
  };

  const login = async (username: string, password: string) => {
    const response = await fetch('/cv-ats/api/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Login failed');
    }

    const data = await response.json();
    const { access, refresh, user: userData } = data;

    // Store tokens
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(userData));

    setToken(access);
    setUser(userData);
  };

  const logout = async () => {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    try {
      await fetch('/cv-ats/api/auth/logout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with client-side logout even if server request fails
    }

    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');

    setToken(null);
    setUser(null);
  };

  const refreshToken = async () => {
    const storedRefresh = localStorage.getItem('refresh_token');
    if (!storedRefresh) {
      throw new Error('No refresh token available');
    }

    const response = await fetch('/cv-ats/api/auth/token/refresh/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: storedRefresh }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    const { access } = data;

    localStorage.setItem('access_token', access);
    setToken(access);
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token,
    loading,
    login,
    register,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};