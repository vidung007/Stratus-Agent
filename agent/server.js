// server.js

// 1. Import Dependencies
require('dotenv').config(); // Loads environment variables from .env file
const express = require('express');
const session = require('express-session');
const axios = require('axios');
const path = require('path');

// 2. Initialize Express App and Load Config
const app = express();
app.set('view engine', 'ejs');
const PORT = 3000;

const { 
  COGNITO_DOMAIN, 
  COGNITO_CLIENT_ID, 
  COGNITO_CLIENT_SECRET, 
  CALLBACK_URL 
} = process.env;

// 3. Configure Session Middleware
// This creates a cookie to keep the user logged in.
app.use(session({
  secret: 'a-super-secret-key-that-should-be-in-env', // In production, use a long, random string from your .env file
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } // In production, set this to true if using HTTPS
}));

app.use(express.urlencoded({ extended: true }));

// 4. Define Authentication Routes

// Redirects the user to the Cognito Hosted UI for login
app.get('/login', (req, res) => {
  const loginUrl = new URL(`${COGNITO_DOMAIN}/login`);
  loginUrl.searchParams.append('response_type', 'code');
  loginUrl.searchParams.append('client_id', COGNITO_CLIENT_ID);
  loginUrl.searchParams.append('redirect_uri', CALLBACK_URL);
  loginUrl.searchParams.append('scope', 'openid profile email');
  res.redirect(loginUrl.toString());
});

// Cognito redirects back to this route after a successful login
app.get('/auth/callback', async (req, res) => {
  const { code } = req.query;

  if (!code) {
    return res.status(400).send('Error: Authorization code not found.');
  }

  try {
    // Exchange the authorization code for tokens
    const tokenUrl = new URL(`${COGNITO_DOMAIN}/oauth2/token`);
    const response = await axios.post(
      tokenUrl.toString(),
      new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: COGNITO_CLIENT_ID,
        client_secret: COGNITO_CLIENT_SECRET,
        redirect_uri: CALLBACK_URL,
        code: code,
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );

    // Store tokens in the session
    req.session.tokens = response.data;
    
    // For simplicity, we can fetch user info here or decode the id_token
    // Let's get user info from the /oauth2/userInfo endpoint
    const userInfoUrl = new URL(`${COGNITO_DOMAIN}/oauth2/userInfo`);
    const userResponse = await axios.get(userInfoUrl.toString(), {
        headers: {
            'Authorization': `Bearer ${req.session.tokens.access_token}`
        }
    });
    
    // Store user info in the session
    req.session.user = userResponse.data;

    // Redirect to the homepage
    res.redirect('/');

  } catch (error) {
    console.error('Error exchanging code for tokens:', error.response ? error.response.data : error.message);
    res.status(500).send('Authentication failed.');
  }
});

// Logs the user out
app.get('/logout', (req, res) => {
  const logoutUrl = new URL(`${COGNITO_DOMAIN}/logout`);
  logoutUrl.searchParams.append('client_id', COGNITO_CLIENT_ID);
  logoutUrl.searchParams.append('logout_uri', `http://localhost:${PORT}/login`); // Redirect to login after logout
  
  // Destroy the local session
  req.session.destroy(err => {
    if (err) {
      return res.status(500).send('Could not log out.');
    }
    // Redirect to Cognito's logout page
    res.redirect(logoutUrl.toString());
  });
});

// 5. Define a Middleware to Protect Routes
const isAuthenticated = (req, res, next) => {
  if (req.session.user) {
    // If user is in the session, proceed
    return next();
  }
  // If not, redirect to login
  res.redirect('/login');
};

// 6. Define Application Routes

// The homepage is now protected by our 'isAuthenticated' middleware
app.get('/', isAuthenticated, (req, res) => {
  // This line finds views/index.ejs, injects the user object, and sends the HTML
  res.render('index', { user: req.session.user });  
});

// server.js -> Add these inside Section 6

// This route handles the form submission from the UI
app.post('/submit-standard-agent', isAuthenticated, async (req, res) => {
    try {
      const query = req.body.query;
      const apiUrl = process.env.AI_BACKEND_API_URL; // We will add this to .env next
  
      // Call our AI backend's "starter" endpoint
      const response = await axios.post(`${apiUrl}/standard-agent`, { query });
      const { jobId } = response.data;
  
      // Redirect the user to a results page where they can wait
      // res.redirect(`/results/${jobId}`);
      res.json({ jobId });
    } catch (error) {
      console.error('Error starting standard agent job:', error);
      res.status(500).send('Failed to start AI job.');
    }
  });

  app.post('/submit-interleaved-agent', isAuthenticated, async (req, res) => {
    try {
      const query = req.body.query;
      const apiUrl = process.env.AI_BACKEND_API_URL;
  
      // Call the interleaved agent's "starter" endpoint
      const response = await axios.post(`${apiUrl}/interleaved-agent`, { query });
      const { jobId } = response.data;
  
      // Redirect to the same results page to show progress
      // res.redirect(`/results/${jobId}`);
      res.json({ jobId });

    } catch (error) {
      console.error('Error starting interleaved agent job:', error);
      res.status(500).send('Failed to start AI job.');
    }
  });
  
  // This route displays the waiting page for a specific job
  // app.get('/results/:jobId', isAuthenticated, (req, res) => {
  //   res.render('results', { jobId: req.params.jobId, user: req.session.user });
  // });
  
  // This is an API endpoint for the waiting page to check the job status
  app.get('/status/:jobId', isAuthenticated, async (req, res) => {
    try {
      const { jobId } = req.params;
      const apiUrl = process.env.AI_BACKEND_API_URL;
  
      // Call our AI backend's "status checker" endpoint
      const response = await axios.get(`${apiUrl}/get-job-status?jobId=${jobId}`);
  
      // Send the status back to the browser
      res.json(response.data);
    } catch (error) {
      console.error('Error checking job status:', error);
      res.status(500).json({ status: 'FAILED', result: 'Could not retrieve job status.' });
    }
  });

// 7. Start the Server
app.listen(PORT, () => {
  console.log(`Server is running at http://localhost:${PORT}`);
});