// src/AgentInterface.jsx
import React, { useState } from 'react';

// NOTE: We need to pass the base URL of our Express BFF server
const API_BASE_URL = 'http://localhost:3000'; 

const AgentInterface = ({ user }) => {
  const [standardResult, setStandardResult] = useState('');
  const [interleavedResult, setInterleavedResult] = useState('');
  const [standardStatus, setStandardStatus] = useState('');
  const [interleavedStatus, setInterleavedStatus] = useState('');

  const handleJobSubmit = async (query, agentType, setStatus, setResult) => {
    if (!query) return;
    setStatus('Submitting job...');
    setResult('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/submit-job`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ query, agentType }),
      });
      if (!response.ok) throw new Error(`Server responded with status ${response.status}`);
      
      const data = await response.json();
      pollForResult(data.jobId, setStatus, setResult);
    } catch (error) {
      setStatus(`Error starting job: ${error.message}`);
    }
  };

  const pollForResult = (jobId, setStatus, setResult) => {
    setStatus('Job submitted. Your AI agent is thinking...');
    const intervalId = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`, { credentials: 'include' });
        if (!response.ok) throw new Error(`Server responded with status ${response.status}`);
        
        const data = await response.json();
        if (data.status === 'COMPLETE') {
          clearInterval(intervalId);
          setStatus('');
          setResult(data.result);
        } else if (data.status === 'FAILED') {
          clearInterval(intervalId);
          setStatus(`Job Failed: ${data.result}`);
        }
      } catch (error) {
        clearInterval(intervalId);
        setStatus(`An error occurred while fetching the result: ${error.message}`);
      }
    }, 5000);
  };

  return (
    <div>
      <div className="agent-section">
        <h2>Standard Agent Orchestrator</h2>
        <form onSubmit={(e) => {
          e.preventDefault();
          handleJobSubmit(e.target.elements.query.value, 'standard', setStandardStatus, setStandardResult);
        }}>
          <textarea name="query" placeholder="e.g., 'Plan a 5-day culinary tour of Italy'" rows="3" required></textarea>
          <button type="submit">Submit</button>
        </form>
        <div className="result-box">
          <p className="status">{standardStatus}</p>
          <pre>{standardResult}</pre>
        </div>
      </div>
      <div className="agent-section">
        <h2>Interleaved Thinking Orchestrator</h2>
        <form onSubmit={(e) => {
          e.preventDefault();
          handleJobSubmit(e.target.elements.query.value, 'interleaved', setInterleavedStatus, setInterleavedResult);
        }}>
          <textarea name="query" placeholder="e.g., 'Analyze the impact of remote work on productivity'" rows="3" required></textarea>
          <button type="submit">Submit</button>
        </form>
        <div className="result-box">
          <p className="status">{interleavedStatus}</p>
          <pre>{interleavedResult}</pre>
        </div>
      </div>
    </div>
  );
};

export default AgentInterface;