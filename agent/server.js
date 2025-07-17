// agent-express-backend/server.js

require('dotenv').config();
const express = require('express');
const session = require('express-session');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Get credentials from the .env file
const { 
  COGNITO_DOMAIN, 
  COGNITO_CLIENT_ID, 
  COGNITO_CLIENT_SECRET, 
  CALLBACK_URL,
  AI_BACKEND_API_URL 
} = process.env;


// --- Middleware Setup ---
app.use(cors({
    origin: 'http://localhost:5173', // Address of your React dev server
    credentials: true // Allows session cookies to be sent
}));
app.use(express.json()); // Middleware to parse incoming JSON requests
app.use(session({
  secret: 'a-super-secret-key-that-should-be-in-env',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } 
}));


// --- Authentication Routes (for browser redirects) ---

app.get('/login', (req, res) => {
  const loginUrl = new URL(`${COGNITO_DOMAIN}/login`);
  loginUrl.searchParams.append('response_type', 'code');
  loginUrl.searchParams.append('client_id', COGNITO_CLIENT_ID);
  loginUrl.searchParams.append('redirect_uri', CALLBACK_URL);
  loginUrl.searchParams.append('scope', 'openid profile email');
  res.redirect(loginUrl.toString());
});

app.get('/logout', (req, res) => {
  const logoutUrl = new URL(`${COGNITO_DOMAIN}/logout`);
  logoutUrl.searchParams.append('client_id', COGNITO_CLIENT_ID);
  logoutUrl.searchParams.append('logout_uri', 'http://localhost:5173'); 
  
  req.session.destroy(() => {
    res.redirect(logoutUrl.toString());
  });
});

app.get('/auth/callback', async (req, res) => {
  const { code } = req.query;
  try {
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
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );
    req.session.tokens = response.data;
    
    const userInfoUrl = new URL(`${COGNITO_DOMAIN}/oauth2/userInfo`);
    const userResponse = await axios.get(userInfoUrl.toString(), {
        headers: { 'Authorization': `Bearer ${req.session.tokens.access_token}` }
    });
    req.session.user = userResponse.data;
    
    res.redirect('http://localhost:5173'); 
  } catch (error) {
    console.error('Authentication failed:', error.response ? error.response.data : error.message);
    res.redirect('http://localhost:5173');
  }
});


// --- JSON API Routes (for the React app's 'fetch' requests) ---

const isAuthenticated = (req, res, next) => {
    if (req.session.user) {
        return next();
    }
    res.status(401).json({ error: 'Not authenticated' });
};

app.get('/api/auth/status', (req, res) => {
    res.json({ user: req.session.user || null });
});

// A single endpoint to start jobs for BOTH agents
app.post('/api/submit-job', isAuthenticated, async (req, res) => {
    try {
        const { query, agentType } = req.body;
        // Determine the correct backend endpoint based on agentType
        const endpoint = agentType === 'interleaved' ? '/interleaved-agent' : '/standard-agent';
        
        const response = await axios.post(`${AI_BACKEND_API_URL}${endpoint}`, { query });
        res.json({ jobId: response.data.jobId });
    } catch (error) {
        console.error(`Error starting ${req.body.agentType} job:`, error);
        res.status(500).json({ error: 'Failed to start AI job.' });
    }
});

app.get('/api/status/:jobId', isAuthenticated, async (req, res) => {
    try {
        const { jobId } = req.params;
        const response = await axios.get(`${AI_BACKEND_API_URL}/get-job-status?jobId=${jobId}`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ status: 'FAILED', result: 'Could not retrieve job status.' });
    }
});


app.listen(PORT, () => {
    console.log(`Express server is running at http://localhost:${PORT}`);
});