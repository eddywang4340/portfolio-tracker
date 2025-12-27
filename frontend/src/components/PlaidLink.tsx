import { usePlaidLink } from 'react-plaid-link';
import { useEffect, useState } from 'react';
import axios from 'axios';

const PlaidLink = ({ onSuccess }: { onSuccess: () => void}) => {
    const [linkToken, setLinkToken] = useState<string | null>(null);

    useEffect(() => {
        axios.post('http://localhost:8000/plaid/create_link_token')
            .then(res => setLinkToken(res.data.link_token));
    }, []);

    const { open, ready } = usePlaidLink({
        token: linkToken,
        onSuccess: async (public_token) => {
            await axios.post('http://localhost:8000/plaid/exchange_public_token', {
                public_token
            });
            onSuccess();
        },
    });

    return (
        <button onClick={() => open()} disabled={!ready}>
            Connect Your Account
        </button>
    );
};

export default PlaidLink;
