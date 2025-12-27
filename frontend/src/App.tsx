import { useState } from 'react';
import PlaidLink from './components/PlaidLink';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [userId, setUserId] = useState<number | null>(null);
  const [useTestUser, setUseTestUser] = useState(false);

  const handlePlaidSuccess = (newUserId: number) => {
    setUserId(newUserId);
  };

  const handleUseTestUser = () => {
    setUserId(1); // Assuming 1 is the test user ID
    setUseTestUser(true);
  };

  return (
    <div className="App">
      {!userId ? (
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '100vh',
          gap: '20px'
        }}>
          <h1>Portfolio Tracker</h1>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Connect your investment account to track your portfolio
          </p>
          
          <PlaidLink onSuccess={handlePlaidSuccess} />
          
          <div style={{ marginTop: '20px' }}>
            <p style={{ color: '#999', fontSize: '14px' }}>Or for testing:</p>
            <button
              onClick={handleUseTestUser}
              style={{
                padding: '8px 16px',
                backgroundColor: '#f0f0f0',
                color: '#333',
                border: '1px solid #ccc',
                borderRadius: '4px',
                cursor: 'pointer',
                marginTop: '10px'
              }}
            >
              Use Test Portfolio
            </button>
          </div>
        </div>
      ) : (
        <Dashboard userId={userId} />
      )}
    </div>
  );
}

export default App;
