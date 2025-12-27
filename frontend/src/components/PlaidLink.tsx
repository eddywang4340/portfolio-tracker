import { usePlaidLink } from 'react-plaid-link';
import { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface PlaidLinkProps {
    onSuccess: (userId: number) => void;
}

const PlaidLink = ({ onSuccess }: PlaidLinkProps) => {
    const [linkToken, setLinkToken] = useState<string | null>(null);

    useEffect(() => {
        axios.get(`${API_URL}/plaid/create_link_token`)
            .then(res => setLinkToken(res.data.link_token))
            .catch(err => console.error('Error creating link token:', err));
    }, []);

    const { open, ready } = usePlaidLink({
        token: linkToken,
        onSuccess: async (public_token: string) => {
            try {
                const response = await axios.post(`${API_URL}/plaid/exchange_public_token`, {
                    public_token
                });
                const userId = response.data.user_id;
                onSuccess(userId);
            } catch (err) {
                console.error('Error exchanging public token:', err);
            }
        },
    });

    return (
    <button 
      onClick={() => open()} 
      disabled={!ready}
      style={{
        padding: '12px 24px',
        fontSize: '16px',
        backgroundColor: ready ? '#0066cc' : '#ccc',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: ready ? 'pointer' : 'not-allowed'
      }}
    >
      Connect Your Account
    </button>
  );
};

export default PlaidLink;
