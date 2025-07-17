// src/components/WelcomePage.jsx
import React, { useEffect } from 'react';
import './WelcomePage.css'; // We will create this CSS file next

const WelcomePage = ({ onSignIn }) => {
  // This effect hook will run once to create the starfield animation
  useEffect(() => {
    const starfield = document.querySelector('.starfield');
    // Prevent adding stars if they already exist
    if (starfield.childElementCount > 0) return;

    for (let i = 0; i < 150; i++) {
      const star = document.createElement('div');
      star.className = 'star';
      const size = Math.random() * 2 + 1;
      star.style.width = `${size}px`;
      star.style.height = `${size}px`;
      star.style.top = `${Math.random() * 100}%`;
      star.style.left = `${Math.random() * 100}%`;
      const duration = Math.random() * 3 + 2;
      star.style.animationDuration = `${duration}s`;
      const delay = Math.random() * 3;
      star.style.animationDelay = `${delay}s`;
      starfield.appendChild(star);
    }
  }, []);

  return (
    <div className="welcome-wrapper">
      <div className="starfield"></div>
      <div className="welcome-container">
        <h1>ProfitPoint Negotiator</h1>
        <p>Harnessing advanced AI to forge the perfect deal. Unlock optimal promotions and maximize profitability for distributors and retailers alike.</p>
        
        {/* Changed from an <a> tag to a button with an onClick handler */}
        <button onClick={onSignIn} className="cta-button">Get Started</button>
      </div>
    </div>
  );
};

export default WelcomePage;