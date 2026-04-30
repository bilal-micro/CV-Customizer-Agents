import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const RegistrationForm: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { register } = useAuth();

  // Validation states
  const [usernameError, setUsernameError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [confirmPasswordError, setConfirmPasswordError] = useState<string | null>(null);

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const getPasswordStrength = (password: string): { strength: string; color: string; percentage: number } => {
    if (password.length === 0) return { strength: '', color: '', percentage: 0 };
    
    let score = 0;
    if (password.length >= 6) score += 1;
    if (password.length >= 10) score += 1;
    if (password.length >= 12) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    const percentage = (score / 6) * 100;
    
    if (percentage < 40) return { strength: 'Weak', color: '#ef4444', percentage };
    if (percentage < 70) return { strength: 'Medium', color: '#f59e0b', percentage };
    return { strength: 'Strong', color: '#10b981', percentage };
  };

  const validateForm = (): boolean => {
    let isValid = true;

    // Username validation
    if (username.length < 3) {
      setUsernameError('Username must be at least 3 characters');
      isValid = false;
    } else {
      setUsernameError(null);
    }

    // Email validation
    if (!validateEmail(email)) {
      setEmailError('Please enter a valid email address');
      isValid = false;
    } else {
      setEmailError(null);
    }

    // Password validation
    if (password.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      isValid = false;
    } else {
      setPasswordError(null);
    }

    // Confirm password validation
    if (password !== confirmPassword) {
      setConfirmPasswordError('Passwords do not match');
      isValid = false;
    } else {
      setConfirmPasswordError(null);
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      await register(username, email, password);
      setSuccess(true);
      setError(null);
      // Redirect will be handled by the parent component
      setTimeout(() => {
        window.location.href = '/cv-ats/login';
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const passwordStrength = getPasswordStrength(password);

  return (
    <form onSubmit={handleSubmit} className="registration-form">
      <div className="form-group">
        <label htmlFor="username">Username</label>
        <input
          type="text"
          id="username"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value);
            setUsernameError(null);
          }}
          required
          disabled={loading}
          placeholder="Choose a username"
          className={`form-input ${usernameError ? 'error' : ''}`}
        />
        {usernameError && <div className="field-error animate-shake">⚠️ {usernameError}</div>}
      </div>

      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            setEmailError(null);
          }}
          required
          disabled={loading}
          placeholder="your@email.com"
          className={`form-input ${emailError ? 'error' : ''}`}
        />
        {emailError && <div className="field-error animate-shake">⚠️ {emailError}</div>}
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <div className="password-input-wrapper">
          <input
            type={showPassword ? 'text' : 'password'}
            id="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setPasswordError(null);
            }}
            required
            disabled={loading}
            placeholder="Create a password"
            className={`form-input ${passwordError ? 'error' : ''}`}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="password-toggle"
            disabled={loading}
          >
            {showPassword ? '🙈' : '👁️'}
          </button>
        </div>
        {password && (
          <div className="password-strength">
            <div className="password-strength-label">
              <span>Password strength: </span>
              <span style={{ color: passwordStrength.color, fontWeight: 'bold', marginLeft: '8px' }}>
                {passwordStrength.strength}
              </span>
            </div>
            <div className="password-strength-bar">
              <div 
                className="password-strength-fill" 
                style={{ 
                  width: `${passwordStrength.percentage}%`,
                  backgroundColor: passwordStrength.color
                }}
              />
            </div>
          </div>
        )}
        {passwordError && <div className="field-error animate-shake">⚠️ {passwordError}</div>}
      </div>

      <div className="form-group">
        <label htmlFor="confirmPassword">Confirm Password</label>
        <div className="password-input-wrapper">
          <input
            type={showConfirmPassword ? 'text' : 'password'}
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              setConfirmPasswordError(null);
            }}
            required
            disabled={loading}
            placeholder="Confirm your password"
            className={`form-input ${confirmPasswordError ? 'error' : ''}`}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="password-toggle"
            disabled={loading}
          >
            {showConfirmPassword ? '🙈' : '👁️'}
          </button>
        </div>
        {confirmPasswordError && <div className="field-error animate-shake">⚠️ {confirmPasswordError}</div>}
      </div>

      {error && (
        <div className="error-message animate-shake">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {success && (
        <div className="success-message animate-success">
          <span className="success-icon">✅</span>
          Registration successful! Redirecting to login...
        </div>
      )}

      <button 
        type="submit" 
        disabled={loading || success || !username || !email || !password || !confirmPassword} 
        className="submit-button"
      >
        {loading ? (
          <>
            <span className="spinner"></span>
            Creating account...
          </>
        ) : success ? (
          <>
            <span className="success-icon">✅</span>
            Success!
          </>
        ) : (
          <>
            🚀 Create Account
          </>
        )}
      </button>
    </form>
  );
};

export default RegistrationForm;
