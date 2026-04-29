import { useState } from 'react';
import { BrowserRouter, Link, Route, Routes, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import JobForm from './components/JobForm';
import ProcessList from './components/ProcessList';
import ProcessDetail from './pages/ProcessDetail';
import ProfilePage from './pages/ProfilePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import './App.css';

function NavLinks() {
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const isActive = (path: string) => location.pathname === path;
  
  const handleLogoutClick = () => {
    setShowLogoutConfirm(true);
  };
  
  const confirmLogout = async () => {
    setIsLoggingOut(true);
    setShowLogoutConfirm(false);
    try {
      await logout();
    } finally {
      setIsLoggingOut(false);
    }
  };
  
  const cancelLogout = () => {
    setShowLogoutConfirm(false);
  };
  
  // Get user initials for avatar
  const getUserInitials = () => {
    if (user?.username) {
      return user.username.slice(0, 2).toUpperCase();
    }
    return 'U';
  };
  
  if (!isAuthenticated) {
    return null;
  }
  
  return (
    <>
      <div className="nav-links">
        <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>🚀 New Analysis</Link>
        <Link to="/history" className={`nav-link ${isActive('/history') ? 'active' : ''}`}>📋 History</Link>
        <Link to="/profile" className={`nav-link ${isActive('/profile') ? 'active' : ''}`}>👤 Profile</Link>
        <div className="user-section">
          <div className="user-avatar">{getUserInitials()}</div>
          <span className="user-info">{user?.username}</span>
        </div>
        <button 
          onClick={handleLogoutClick} 
          className="nav-link logout-link"
          disabled={isLoggingOut}
          aria-label="Logout"
        >
          {isLoggingOut ? (
            <>
              <span className="logout-spinner"></span>
              Logging out...
            </>
          ) : (
            <>
              <span className="logout-icon">🚪</span>
              Logout
            </>
          )}
        </button>
      </div>
      
      {showLogoutConfirm && (
        <div className="logout-modal-overlay" onClick={cancelLogout}>
          <div className="logout-modal" onClick={(e) => e.stopPropagation()}>
            <div className="logout-modal-header">
              <span className="logout-modal-icon">⚠️</span>
              <h3>Confirm Logout</h3>
            </div>
            <p className="logout-modal-message">
              Are you sure you want to logout? You'll need to login again to access your account.
            </p>
            <div className="logout-modal-actions">
              <button onClick={cancelLogout} className="logout-modal-cancel">
                Cancel
              </button>
              <button onClick={confirmLogout} className="logout-modal-confirm">
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="app">
          <nav className="navbar">
            <Link to="/" className="nav-brand">ATS Agentic</Link>
            <NavLinks />
          </nav>
          <main className="main-content">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/" element={<JobForm />} />
              <Route path="/history" element={<ProcessList />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/process/:id" element={<ProcessDetail />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
