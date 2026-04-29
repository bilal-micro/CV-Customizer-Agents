import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import RegistrationForm from '../components/RegistrationForm';

const RegisterPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="register-page">
      <div className="register-container animate-fade-in">
        <div className="register-header">
          <h1 className="register-title">🎯 ATS Agentic</h1>
          <p className="register-subtitle">
            Create your account to start optimizing your CV with AI-powered ATS analysis.
          </p>
        </div>
        <div className="register-form-wrapper">
          <h2 className="form-title">Create Account</h2>
          <RegistrationForm />
        </div>
        <div className="register-links">
          <p>
            Already have an account?{' '}
            <a href="/login" className="auth-link">
              Login here
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
