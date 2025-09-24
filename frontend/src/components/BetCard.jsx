// frontend/src/components/BetCard.jsx
import React from 'react';
import axios from 'axios';

function BetCard({ bet }) {
  const [votes, setVotes] = React.useState(0);

  React.useEffect(() => {
    const fetchVotes = async () => {
      const response = await axios.get(`http://localhost:4000/api/bets/${bet.id}/vote`, { method: 'POST', data: { option: 'yes' } });
      setVotes(response.data.id);
    };

    fetchVotes();
  }, [bet.id]);

  return (
    <div style={{ border: '1px solid #ccc', padding: '10px', margin: '10px' }}>
      <h3>{bet.title}</h3>
      <p>{bet.description}</p>
      <p>End Date: {bet.endDate}</p>
      <button onClick={() => {
        fetch(`http://localhost:4000/api/bets/${bet.id}/vote`, { method: 'POST', data: { option: 'no' } });
      }}>Vote No</button>
    </div>
  );
}

export default BetCard;