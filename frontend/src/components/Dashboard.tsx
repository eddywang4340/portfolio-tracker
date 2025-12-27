import { useEffect, useState } from 'react';
import axios from 'axios';

interface Position {
    symbol: string;
    quantity: number;
    current_price: number;
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

const Dashboard = ({ userId }: { userId: number }) => {
    const [portfolio, setPortfolio] = useState<Portfolio | null>(null);

    useEffect(() => {
        loadPortfolio();
    }, [userId]);

    const loadPortfolio = async () => {
        const res = await axios.get('https://localhost:8000/plaid/portfolio/${userId');
        setPortfolio(res.data);
    };

    if (!portfolio) return <div>Loading...</div>

    return (
        <div className="dashboard">
            <div className="summary">
                <h2>Portfolio Value: ${portfolio.total_value.toFixed(2)}</h2>
                <p>Total Gain/Loss: ${portfolio.total_gain_loss.toFixed(2)} ({portfolio.total_gain_loss_pct.toFixed(2)}%)</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Value</th>
                        <th>Gain/Loss</th>
                    </tr>
                </thead>
                <tbody>
                    {portfolio.positions.map(pos => (
                        <tr key={pos.symbol}>
                            <td>{pos.symbol}</td>
                            <td>{pos.quantity}</td>
                            <td>${pos.current_price.toFixed(2)}</td>
                            <td>${pos.current_value.toFixed(2)}</td>
                            <td className={pos.gain_loss >= 0 ? 'positive' : 'negative'}>
                                ${pos.gain_loss.toFixed(2)} ({pos.gain_loss_pct.toFixed(2)}%)
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Dashboard;