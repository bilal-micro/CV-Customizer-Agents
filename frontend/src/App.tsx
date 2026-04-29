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
  const isActive = (path: string) => location.pathname === path;
  
  const handleLogout = async () => {
    await logout();
  };
  
  if (!isAuthenticated) {
    return null;
  }
  
  return (
    <div className="nav-links">
      <Link to="/" className={isActive('/') ? 'active' : ''}>🚀 New Analysis</Link>
      <Link to="/history" className={isActive('/history') ? 'active' : ''}>📋 History</Link>
      <Link to="/profile" className={isActive('/profile') ? 'active' : ''}>👤 Profile</Link>
      <span className="user-info">Welcome, {user?.username}</span>
      <button onClick={handleLogout} className="logout-btn">Logout</button>
    </div>
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
