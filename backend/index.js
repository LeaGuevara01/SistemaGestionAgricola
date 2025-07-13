require('dotenv').config();
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Database connection
const dbPath = path.resolve(__dirname, '../sistema_gestion_agricola.db');
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
  } else {
    console.log('Connected to the SQLite database.');
  }
});

// API route to get maquinas from DB
app.get('/api/maquinas', (req, res) => {
  const query = 'SELECT * FROM maquinas';
  db.all(query, [], (err, rows) => {
    if (err) {
      console.error('Error querying database:', err.message);
      res.status(500).json({ error: 'Database error' });
    } else {
      res.json(rows);
    }
  });
});

app.listen(port, () => {
  console.log(`Backend server running on port ${port}`);
});
