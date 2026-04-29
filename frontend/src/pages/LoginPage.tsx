import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';

const LoginPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="login-page">
      <div className="login-container animate-fade-in">
        <div className="login-header">
          <h1 className="login-title">🎯 ATS Agentic</h1>
          <p className="login-subtitle">Welcome back! Please login to continue.</p>
        </div>
        <div className="login-form-wrapper">
          <h2 className="form-title">Login</h2>
          <LoginForm />
        </div>
        <div className="login-links">
          <p>
            Don't have an account?{' '}
            <a href="/register" className="auth-link">
              Create one here
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
