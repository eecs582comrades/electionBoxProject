console.log("Hello World")

// Name(s): Matthew Petillo, William Johnson, Katie Golder
// Date Created: 3-4-25
// Dates Revised: 3-4-25
// Brief description of each revision & author:

const express = require('express')
const http = require('http');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const path = require('path');
const crypto = require('node:crypto')
const cors = require('cors');
const fs = require('fs')

const app = express();
app.use(cors());
const port = 9100;
const localNetworkHost = '0.0.0.0';

const bcrypt = require('bcrypt');
const saltRounds = 10; // Number of salt rounds for hashing

const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: '',
  database: 'electionbox'
});

connection.connect((err) => {
  if (err) {
    console.error('Error connecting to MySQL:', err);
    return;
  }
  console.log('Connected to MySQL database');
});

http.createServer(app);

app.use(express.static(path.join(__dirname, '../app')));
app.use(express.json());


app.get('/test', (req, res) => { 
  // const ballot_id = req.params.ballot_id;
  connection.query('SELECT * FROM ballots', (err, results) => {
    if (err) {
      console.error('Error fetching ballots:', err);
      res.status(500).send('Server error');
      return;
    }
    res.json(results);
    return;
  });
});

app.post('/envelopeData', (req, res) => {
  console.log(req.data);
  connection.query('INSERT INTO ballots (barcode_data, date, time, location, name) AS (?, ?, ?, ?, ?)', [req.data['IMB'], req.data['DATE'], req.data['TIME'], req.data['LOCATION'], req.data['OCR']], (err, results) => {
    if (err) {
      console.error('Error pushing ballot data:', err);
      res.status(500).send('Server error');
      return;
    }
    res.status(200).send("200 OK");
  });
});

//no
app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});

app.post('/', (req, res) => {
    res.send('Got a POST request')
});

// Registers the app to use bodyParser to make our lives easier and avoid needing to decode json frequently.
app.use(bodyParser.json());