import { useState, useEffect } from 'react'
import './App.css'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';

const API_BASE = 'http://localhost:8000';
const API_KEY = 'your-secret-api-key';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        onLogin(data);
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  return (
    <div className="auth-card">
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className="auth-form">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

function Home({ user, notifications }) {
  return (
    <div className="page-card">
      <h2>Home</h2>
      <p>Hello <strong>{user.name}</strong>, welcome back to the notification dashboard.</p>
      <p>You currently have <strong>{notifications.length}</strong> notification{notifications.length === 1 ? '' : 's'}.</p>
      <p>Use the navigation above to view notifications or sort by priority.</p>
    </div>
  );
}

function Notifications({ notifications, onRefresh }) {
  return (
    <div className="page-card">
      <div className="page-header">
        <h2>Notifications</h2>
        <button onClick={onRefresh}>Refresh</button>
      </div>
      {notifications.length === 0 ? (
        <p className="empty-state">No notifications available.</p>
      ) : (
        <ul className="notification-list">
          {notifications.map((notif) => (
            <li key={notif.id} className="notification-item">
              <div className="notification-top">
                <span className="notification-type">{notif.type}</span>
                <span className="notification-priority">Priority {notif.priority}</span>
              </div>
              <p className="notification-message">{notif.message}</p>
              {notif.timestamp && <span className="notification-time">{new Date(notif.timestamp).toLocaleString()}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState('');

  const fetchNotifications = async () => {
    if (!user) return;
    setError('');

    try {
      const response = await fetch(`${API_BASE}/sort_by_priority`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-KEY': API_KEY,
        },
        body: JSON.stringify({ user_id: user.user_id }),
      });
      const data = await response.json();
      if (response.ok) {
        setNotifications(data.notifications || []);
      } else {
        setError(data.detail || 'Unable to fetch notifications');
      }
    } catch (err) {
      setError('Network error while fetching notifications');
    }
  };

  useEffect(() => {
    if (user) {
      fetchNotifications();
      const intervalId = setInterval(fetchNotifications, 5 * 60 * 1000);
      return () => clearInterval(intervalId);
    }
  }, [user]);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    setNotifications([]);
    setError('');
  };

  return (
    <Router>
      <div className="app-shell">
        {!user ? (
          <div className="center-screen">
            <Login onLogin={handleLogin} />
          </div>
        ) : (
          <div className="app-layout">
            <header className="app-header">
              <div>
                <h1>Notification Dashboard</h1>
                <p className="subtext">Logged in as {user.name} ({user.email})</p>
              </div>
              <button className="logout-button" onClick={handleLogout}>Logout</button>
            </header>

            <nav className="app-nav">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/notifications" className="nav-link">Notifications</Link>
              <button className="nav-button" onClick={fetchNotifications}>Sort by Priority</button>
            </nav>

            {error && <div className="error-banner">{error}</div>}

            <main className="app-content">
              <Routes>
                <Route path="/" element={<Home user={user} notifications={notifications} />} />
                <Route path="/notifications" element={<Notifications notifications={notifications} onRefresh={fetchNotifications} />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App
