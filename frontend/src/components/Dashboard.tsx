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
    onSignOut: () => void;
    isTestMode?: boolean;
}

const Dashboard = ({ userId, onSignOut, isTestMode = false }: DashboardProps) => {
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
        <div style={{ minHeight: '100vh', backgroundColor: '#fafafa' }}>
            {/* Navigation Header */}
            <div style={{
                backgroundColor: 'white',
                borderBottom: '1px solid #e5e7eb',
                padding: '16px 24px',
                position: 'sticky',
                top: 0,
                zIndex: 1000,
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
            }}>
                <div style={{
                    maxWidth: '1200px',
                    margin: '0 auto',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: '600' }}>
                            Portfolio Tracker
                        </h1>
                        {isTestMode && (
                            <span style={{
                                backgroundColor: '#fef3c7',
                                color: '#92400e',
                                padding: '4px 12px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                fontWeight: '500'
                            }}>
                                Test Mode
                            </span>
                        )}
                    </div>
                    <button
                        onClick={onSignOut}
                        style={{
                            padding: '8px 16px',
                            backgroundColor: '#f3f4f6',
                            color: '#374151',
                            border: '1px solid #d1d5db',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '500',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = '#e5e7eb';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = '#f3f4f6';
                        }}
                    >
                        ← Back to Home
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
                <div style={{ marginBottom: '30px', marginTop: '10px' }}>
                    <button 
                        onClick={loadPortfolio}
                        style={{
                            padding: '10px 20px',
                            backgroundColor: '#0066cc',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '500',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = '#0052a3';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = '#0066cc';
                        }}
                    >
                        🔄 Refresh Portfolio
                    </button>
                </div>

                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr 1fr', 
                    gap: '20px',
                    marginBottom: '40px' 
                }}>
                    <div style={{ 
                        padding: '24px', 
                        backgroundColor: 'white',
                        borderRadius: '12px',
                        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                    }}>
                        <h3 style={{ margin: '0 0 8px 0', color: '#6b7280', fontSize: '14px', fontWeight: '500' }}>
                            Total Value
                        </h3>
                        <p style={{ fontSize: '36px', fontWeight: '700', margin: '0', color: '#111827' }}>
                            ${portfolio.total_value.toFixed(2)}
                        </p>
                    </div>
                    
                    <div style={{ 
                        padding: '24px', 
                        backgroundColor: portfolio.total_gain_loss >= 0 ? '#ecfdf5' : '#fef2f2',
                        borderRadius: '12px',
                        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                    }}>
                        <h3 style={{ margin: '0 0 8px 0', color: '#6b7280', fontSize: '14px', fontWeight: '500' }}>
                            Total Gain/Loss
                        </h3>
                        <p style={{ 
                            fontSize: '36px', 
                            fontWeight: '700', 
                            margin: '0',
                            color: portfolio.total_gain_loss >= 0 ? '#059669' : '#dc2626'
                        }}>
                            ${portfolio.total_gain_loss.toFixed(2)}
                        </p>
                        <p style={{ 
                            fontSize: '18px', 
                            margin: '4px 0 0 0',
                            color: portfolio.total_gain_loss >= 0 ? '#059669' : '#dc2626'
                        }}>
                            {portfolio.total_gain_loss >= 0 ? '+' : ''}{portfolio.total_gain_loss_pct.toFixed(2)}%
                        </p>
                    </div>
                </div>

                {portfolio.positions.length > 0 && (
                    <div style={{ marginBottom: '40px' }}>
                        <h2 style={{ marginBottom: '20px' }}>Asset Allocation</h2>
                        <div style={{ 
                            backgroundColor: 'white',
                            padding: '24px',
                            borderRadius: '12px',
                            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                        }}>
                            <AllocationChart positions={portfolio.positions} />
                        </div>
                    </div>
                )}

                <div>
                    <h2 style={{ marginBottom: '20px' }}>Holdings</h2>
                    <div style={{
                        backgroundColor: 'white',
                        borderRadius: '12px',
                        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                        overflow: 'hidden'
                    }}>
                        <table style={{ 
                            width: '100%', 
                            borderCollapse: 'collapse'
                        }}>
                            <thead>
                                <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
                                    <th style={{ padding: '16px', textAlign: 'left', fontWeight: '600', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Symbol</th>
                                    <th style={{ padding: '16px', textAlign: 'right', fontWeight: '600', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Quantity</th>
                                    <th style={{ padding: '16px', textAlign: 'right', fontWeight: '600', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Price</th>
                                    <th style={{ padding: '16px', textAlign: 'right', fontWeight: '600', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Value</th>
                                    <th style={{ padding: '16px', textAlign: 'right', fontWeight: '600', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Gain/Loss</th>
                                </tr>
                            </thead>
                            <tbody>
                                {portfolio.positions.map(pos => (
                                    <>
                                        <tr 
                                            key={pos.symbol} 
                                            style={{ 
                                                borderBottom: '1px solid #f3f4f6',
                                                cursor: 'pointer',
                                                backgroundColor: expandedSymbol === pos.symbol ? '#f9fafb' : 'transparent',
                                                transition: 'background-color 0.2s'
                                            }}
                                            onClick={() => setExpandedSymbol(expandedSymbol === pos.symbol ? null : pos.symbol)}
                                            onMouseEnter={(e) => {
                                                if (expandedSymbol !== pos.symbol) {
                                                    e.currentTarget.style.backgroundColor = '#fafafa';
                                                }
                                            }}
                                            onMouseLeave={(e) => {
                                                if (expandedSymbol !== pos.symbol) {
                                                    e.currentTarget.style.backgroundColor = 'transparent';
                                                }
                                            }}
                                        >
                                            <td style={{ padding: '16px', fontWeight: '600', fontSize: '14px' }}>
                                                <span>{pos.symbol}</span>
                                                <span style={{ marginLeft: '8px', fontSize: '12px', color: '#9ca3af' }}>
                                                    {expandedSymbol === pos.symbol ? '▼' : '▶'}
                                                </span>
                                            </td>
                                            <td style={{ padding: '16px', textAlign: 'right', fontSize: '14px' }}>{pos.quantity}</td>
                                            <td style={{ padding: '16px', textAlign: 'right', fontSize: '14px' }}>
                                                {pos.current_price !== null ? (
                                                    `$${pos.current_price.toFixed(2)}`
                                                ) : (
                                                    <span style={{ color: '#9ca3af', fontStyle: 'italic' }}>Price unavailable</span>
                                                )}
                                            </td>
                                            <td style={{ padding: '16px', textAlign: 'right', fontSize: '14px', fontWeight: '500' }}>
                                                {pos.current_price !== null ? (
                                                    `$${pos.current_value.toFixed(2)}`
                                                ) : (
                                                    <span style={{ color: '#9ca3af', fontStyle: 'italic' }}>—</span>
                                                )}
                                            </td>
                                            <td style={{ 
                                                padding: '16px', 
                                                textAlign: 'right',
                                                fontSize: '14px',
                                                color: pos.current_price !== null ? (pos.gain_loss >= 0 ? '#059669' : '#dc2626') : '#9ca3af',
                                                fontWeight: pos.current_price !== null ? '600' : 'normal',
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
            </div>
        </div>
    );
};

export default Dashboard;