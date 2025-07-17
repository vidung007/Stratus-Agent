// src/App.jsx
import React, { useState, useEffect } from 'react';
import WelcomePage from './components/WelcomePage';
import AgentInterface from './AgentInterface'; // Import our new component
import './App.css'; // You can keep some minimal styling here

const API_BASE_URL = 'http://localhost:3000';

function App() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

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

  if (isLoading) {
    return <div>Loading session...</div>;
  }
  
  if (user) {
    return (
      <div className="App">
        <div className="header-nav">
          <p>Welcome, {user.username}! | <button onClick={handleSignOut}>Sign Out</button></p>
        </div>
        <h1>ProfitPoint Negotiator</h1>
        <AgentInterface user={user} />
      </div>
    );
  }

  return <WelcomePage onSignIn={handleSignIn} />;
}

export default App;