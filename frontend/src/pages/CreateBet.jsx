// frontend/src/pages/CreateBet.jsx
import React, { useState } from 'react';
import axios from 'axios';

function CreateBet() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = { title, description, endDate };
    await axios.post('http://localhost:4000/api/bets', data);
    // Reset form fields
    setTitle('');
    setDescription('');
    setEndDate('');
  };

  return (
    <div>
      <h2>Create a Bet</h2>
      <form onSubmit={handleSubmit}>
        <label htmlFor="title">Title:</label>
        <input type="text" id="title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <br />
        <label htmlFor="description">Description:</label>
        <textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} />
        <br />
        <label htmlFor="endDate">End Date:</label>
        <input type="date" id="endDate" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        <br />
        <button type="submit">Create Bet</button>
      </form>
    </div>
  );
}

export default CreateBet;