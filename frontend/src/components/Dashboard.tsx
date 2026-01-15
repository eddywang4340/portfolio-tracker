import { useEffect, useState } from 'react';
import axios from 'axios';
import AllocationChart from './AllocationChart';
import MLInsights from './MLInsights';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface Position {
    symbol: string;
    quantity: number;
    current_price: number | null;
    current_value: number;
    cost_basis: number;
    gain_loss: number;
    gain_loss_pct: number;
}

interface Portfolio {
    total_value: number;
    total_cost: number;
    total_gain_loss: number;
    total_gain_loss_pct: number;
    positions: Position[];
}

interface DashboardProps {
    userId: number;
}

const Dashboard = ({ userId }: DashboardProps) => {
    const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
    const [loading, setLoading] = useState(true);
    const [expandedSymbol, setExpandedSymbol] = useState<string | null>(null);

    useEffect(() => {
        loadPortfolio();
    }, [userId]);

    const loadPortfolio = async () => {
        try {
            setLoading(true);
            await axios.post(`${API_URL}/plaid/sync_portfolio?user_id=${userId}`);
            await axios.post(`${API_URL}/plaid/update_prices/${userId}`);
            const res = await axios.get(`${API_URL}/plaid/portfolio/${userId}`);
            setPortfolio(res.data);
        } catch (err) {
            console.error('Error loading portfolio:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Loading portfolio...</div>;
  }

  if (!portfolio) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Error loading portfolio</div>;
  }

    return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '40px' }}>
        <h1>My Portfolio</h1>
        <button 
          onClick={loadPortfolio}
          style={{
            padding: '8px 16px',
            backgroundColor: '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginTop: '10px'
          }}
        >
          Refresh Portfolio
        </button>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '20px',
        marginBottom: '40px' 
      }}>
        <div style={{ 
          padding: '20px', 
          backgroundColor: '#f5f5f5', 
          borderRadius: '8px' 
        }}>
          <h3>Total Value</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', margin: '10px 0' }}>
            ${portfolio.total_value.toFixed(2)}
          </p>
        </div>
        
        <div style={{ 
          padding: '20px', 
          backgroundColor: portfolio.total_gain_loss >= 0 ? '#e8f5e9' : '#ffebee', 
          borderRadius: '8px' 
        }}>
          <h3>Total Gain/Loss</h3>
          <p style={{ 
            fontSize: '32px', 
            fontWeight: 'bold', 
            margin: '10px 0',
            color: portfolio.total_gain_loss >= 0 ? '#2e7d32' : '#c62828'
          }}>
            ${portfolio.total_gain_loss.toFixed(2)} ({portfolio.total_gain_loss_pct.toFixed(2)}%)
          </p>
        </div>
      </div>

      {portfolio.positions.length > 0 && (
        <div style={{ marginBottom: '40px' }}>
          <h2>Asset Allocation</h2>
          <AllocationChart positions={portfolio.positions} />
        </div>
      )}

      <div>
        <h2>Holdings</h2>
        <table style={{ 
          width: '100%', 
          borderCollapse: 'collapse',
          backgroundColor: 'white',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5' }}>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Symbol</th>
              <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Quantity</th>
              <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Price</th>
              <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Value</th>
              <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Gain/Loss</th>
            </tr>
          </thead>
          <tbody>
            {portfolio.positions.map(pos => (
              <>
                <tr 
                  key={pos.symbol} 
                  style={{ 
                    borderBottom: '1px solid #eee',
                    cursor: 'pointer',
                    backgroundColor: expandedSymbol === pos.symbol ? '#f9fafb' : 'transparent'
                  }}
                  onClick={() => setExpandedSymbol(expandedSymbol === pos.symbol ? null : pos.symbol)}
                >
                  <td style={{ padding: '12px', fontWeight: 'bold' }}>
                    <span>{pos.symbol}</span>
                    <span style={{ marginLeft: '8px', fontSize: '12px', color: '#999' }}>
                      {expandedSymbol === pos.symbol ? '▼' : '▶'}
                    </span>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>{pos.quantity}</td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {pos.current_price !== null ? (
                      `$${pos.current_price.toFixed(2)}`
                    ) : (
                      <span style={{ color: '#999', fontStyle: 'italic' }}>Price unavailable</span>
                    )}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {pos.current_price !== null ? (
                      `$${pos.current_value.toFixed(2)}`
                    ) : (
                      <span style={{ color: '#999', fontStyle: 'italic' }}>—</span>
                    )}
                  </td>
                  <td style={{ 
                    padding: '12px', 
                    textAlign: 'right',
                    color: pos.current_price !== null ? (pos.gain_loss >= 0 ? '#2e7d32' : '#c62828') : '#999',
                    fontWeight: pos.current_price !== null ? 'bold' : 'normal',
                    fontStyle: pos.current_price === null ? 'italic' : 'normal'
                  }}>
                    {pos.current_price !== null ? (
                      `$${pos.gain_loss.toFixed(2)} (${pos.gain_loss_pct.toFixed(2)}%)`
                    ) : (
                      '—'
                    )}
                  </td>
                </tr>
                {expandedSymbol === pos.symbol && pos.current_price !== null && (
                  <tr key={`${pos.symbol}-insights`}>
                    <td colSpan={5} style={{ padding: '0', backgroundColor: '#f9fafb' }}>
                      <MLInsights 
                        symbol={pos.symbol} 
                        currentPrice={pos.current_price} 
                      />
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;