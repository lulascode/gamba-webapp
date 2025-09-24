// backend/db.js
const mysql = require('mysql2');

const db = mysql.createPool({
  host: 'mariadb',
  user: 'root',
  password: 'rootpassword',
  database: 'bethub',
});

module.exports = db;