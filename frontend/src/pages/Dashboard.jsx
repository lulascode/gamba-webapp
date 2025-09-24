// frontend/src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import BetCard from '../components/BetCard';
import axios from 'axios';

function Dashboard() {
  const [bets, setBets] = useState([]);

  useEffect(() => {
    const fetchBets = async () => {
      const response = await axios.get('http://localhost:4000/api/bets');
      setBets(response.data);
    };

    fetchBets();
  }, []);

  return (
    <div>
      <h1>BetHub</h1>
      {bets.map((bet) => (
        <BetCard key={bet.id} bet={bet} />
      ))}
    </div>
  );
}

export default Dashboard;