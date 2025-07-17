// src/App.jsx
import React, { useState, useEffect } from 'react';
import AgentInterface from './AgentInterface';
import './App.css'; // Import our new styles

const API_BASE_URL = 'http://localhost:3000';

function App() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check user session on load
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/status`, { credentials: 'include' });
        const data = await response.json();
        setUser(data.user);
      } catch (error) {
        console.error("Could not fetch auth status", error);
      } finally {
        setIsLoading(false);
      }
    };
    checkAuthStatus();
  }, []);

  const handleSignIn = () => {
    window.location.href = `${API_BASE_URL}/login`;
  };

  const handleSignOut = () => {
    window.location.href = `${API_BASE_URL}/logout`;
  };

  // The main layout with the aurora background
  return (
    <>
      <div className="aurora-bg">
        <div className="blob cyan"></div>
        <div className="blob magenta"></div>
      </div>
    
      <div className="App">
        {isLoading ? (
          <div>Loading...</div>
        ) : user ? (
          <>
            <div className="header-nav">
              <span>Welcome, {user.username}!</span>
              <button onClick={handleSignOut}>Sign Out</button>
            </div>
            <h1>AI Negotiator</h1>
            <AgentInterface user={user} />
          </>
        ) : (
          <div className="welcome-container">
            <h1>AI Negotiator</h1>
            <p>Harnessing advanced AI to forge the perfect deal. Unlock optimal promotions and maximize profitability for distributors and retailers alike.</p>
            <button onClick={handleSignIn} className="cta-button">Get Started</button>
          </div>
        )}
      </div>
    </>
  );
}

export default App;