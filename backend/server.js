const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const seed = require('./seed');

const app = express();
const port = process.env.PORT || 4000;

app.use(bodyParser.json());
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});

// API Routes
app.get('/api/bets', async (req, res) => {
  const connection = mysql.createConnection({
    host: 'mariadb',
    user: 'root',
    password: 'rootpassword',
  });

  try {
    const [rows, fields] = await connection.execute('SELECT * FROM bets');
    const bets = rows;
    res.json(bets);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to fetch bets' });
  } finally {
    connection.end();
  }
});

app.post('/api/bets', async (req, res) => {
  const { title, description, endDate } = req.body;

  const connection = mysql.createConnection({
    host: 'mariadb',
    user: 'root',
    password: 'rootpassword',
  });

  try {
    const [rows, fields] = await connection.execute(
      'INSERT INTO bets (title, description, end_date) VALUES (?, ?, ?)',
      [title, description, endDate]
    );
    res.status(201).json({ id: rows[0].id, title, description, endDate });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to create bet' });
  } finally {
    connection.end();
  }
}
);

app.post('/api/bets/:id/vote', async (req, res) => {
  const betId = req.params.id;
  const { option } = req.body;

  const connection = mysql.createConnection({
    host: 'mariadb',
    user: 'root',
    password: 'rootpassword',
  });

  try {
    const [rows, fields] = await connection.execute(
      'INSERT INTO votes (bet_id, option) VALUES (?, ?)',
      [betId, option]
    );
    res.status(201).json({ id: rows[0].id, bet_id: betId, option });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to vote' });
  } finally {
    connection.end();
  }
}
);
