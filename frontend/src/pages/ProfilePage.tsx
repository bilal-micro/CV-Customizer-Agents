import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getProfile, updateProfile } from '../api';

interface ProfileData {
  openrouter_api_key: string;
  preferred_model: string;
}

const OPENROUTER_MODELS = [
  'openai/gpt-4o',
  'openai/gpt-4o-mini',
  'openai/gpt-4-turbo',
  'anthropic/claude-3-opus',
  'anthropic/claude-3-sonnet',
  'anthropic/claude-3-haiku',
  'google/gemini-pro-1.5',
  'meta-llama/llama-3.1-70b-instruct',
  'meta-llama/llama-3.1-405b-instruct',
];

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [profileData, setProfileData] = useState<ProfileData>({
    openrouter_api_key: '',
    preferred_model: 'openai/gpt-4o-mini',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, authLoading, navigate]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchProfile();
    }
  }, [isAuthenticated]);

  const fetchProfile = async () => {
    try {
      const data = await getProfile();
      setProfileData({
        openrouter_api_key: data.openrouter_api_key || '',
        preferred_model: data.preferred_model || 'openai/gpt-4o-mini',
      });
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      setMessage({ type: 'error', text: 'Failed to load profile data' });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await updateProfile(profileData);
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (error) {
      console.error('Failed to update profile:', error);
      setMessage({ type: 'error', text: 'Failed to update profile' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="loading-container animate-fade-in">Loading profile...</div>;
  }

  return (
    <div className="profile-page animate-fade-in">
      <h1>👤 User Profile</h1>
      
      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="profile-form">
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            value={user?.username || ''}
            disabled
            className="disabled-field"
          />
        </div>

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={user?.email || ''}
            disabled
            className="disabled-field"
          />
        </div>

        <div className="form-group">
          <label htmlFor="openrouter_api_key">
            OpenRouter API Key
            <span className="label-hint">(Optional - Leave empty to use system default)</span>
          </label>
          <input
            id="openrouter_api_key"
            type="password"
            value={profileData.openrouter_api_key}
            onChange={(e) => setProfileData({ ...profileData, openrouter_api_key: e.target.value })}
            placeholder="sk-or-v1-..."
          />
          <p className="field-help">
            Get your API key from{' '}
            <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer">
              OpenRouter
            </a>
          </p>
        </div>

        <div className="form-group">
          <label htmlFor="preferred_model">
            Preferred Model
            <span className="label-hint">(For OpenRouter API)</span>
          </label>
          <select
            id="preferred_model"
            value={profileData.preferred_model}
            onChange={(e) => setProfileData({ ...profileData, preferred_model: e.target.value })}
          >
            {OPENROUTER_MODELS.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
          <p className="field-help">
            Select the AI model you want to use for CV optimization
          </p>
        </div>

        <button type="submit" disabled={saving} className="btn-primary">
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  );
};

export default ProfilePage;