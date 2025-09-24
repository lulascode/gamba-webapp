// backend/seed.js
const db = require('./db');

async function seed() {
  await db.query(
    `
    CREATE TABLE IF NOT EXISTS bets (
      id INT AUTO_INCREMENT PRIMARY KEY,
      title VARCHAR(255) NOT NULL,
      description TEXT,
      end_date DATETIME NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS votes (
      id INT AUTO_INCREMENT PRIMARY KEY,
      bet_id INT NOT NULL,
      option ENUM('yes', 'no') NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (bet_id) REFERENCES bets(id)
    );
    `
  );

  const bet1Data = { title: 'Will it rain tomorrow?', description: 'A simple question about the weather.', endDate: '2025-09-25 12:00:00' };
  const bet2Data = { title: 'Which movie will be a hit?', description: 'Predicting the next blockbuster.', endDate: '2025-10-01 18:00:00' };

  const bet1Result = await db.query(
    'INSERT INTO bets (title, description, end_date) VALUES (?, ?, ?)',
    [bet1Result.insertId, bet1Result.insertId, bet1Result.insertId]
  );

  const bet2Result = await db.query(
    'INSERT INTO bets (title, description, end_date) VALUES (?, ?, ?)',
    [bet2Result.insertId, bet2Result.insertId, bet2Result.insertId]
  );

  console.log('Seed data inserted');
}

// Run the seed function on startup
seed();