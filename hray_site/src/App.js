import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import jwtDecode from 'jwt-decode';
import './App.css';
import LoginScreen from './screens/LoginScreen';
import MainScreen from './screens/MainScreen';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      checkTokenValidity();
    }, 60000); // Check every 60 seconds

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);

  const handleLogin = async () => {
    // Example API call
    const response = await fetch('https://your-auth-api.com/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      // Save token to local storage or state
      localStorage.setItem('token', data.token);
      setIsLoggedIn(true);
    } else {
      alert('Login failed');
    }
  };

  const isTokenExpired = (token) => {
    try {
      const decoded = jwtDecode(token);
      const currentTime = Date.now() / 1000; // Convert to seconds
      return decoded.exp < currentTime;
    } catch (error) {
      return true; // If there's an error decoding, consider the token invalid
    }
  };

  const checkTokenValidity = () => {
    const token = localStorage.getItem('token');
    if (!token || isTokenExpired(token)) {
      alert('Session expired. Please log in again.');
      setIsLoggedIn(false);
      // Optionally, redirect to login page
      // window.location.href = '/login';
    } else {
      setIsLoggedIn(true);
    }
  };

  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route
            path="/"
            element={isLoggedIn ? <Navigate to="/main" /> : <Navigate to="/login" />}
          />
          <Route
            path="/login"
            element={
              <LoginScreen
                username={username}
                setUsername={setUsername}
                password={password}
                setPassword={setPassword}
                handleLogin={handleLogin}
              />
            }
          />
          <Route
            path="/main"
            element={isLoggedIn ? <MainScreen /> : <Navigate to="/login" />}
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
