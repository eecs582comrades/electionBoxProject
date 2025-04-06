console.log("Hello World")

// Name(s): Matthew Petillo, William Johnson, Katie Golder
// Date Created: 3-4-25
// Dates Revised: 3-4-25
// Brief description of each revision & author:
//
// THE FOLLOWING APIs EXIST:
// /search/{plantName}, returns all plants found
// /search/{plantId}, returns all plants found
// /account/pull/{username}/{password}, returns account if it exists
// /account/add/{username}/{password}, returns 201 if works
// /account/change/{username}/{oldpassword}/{newpassword}, changes password
// /simulations/{user_id}, returns all simulations found under that user Id
// /simulations/delete/{simulation_id}, deletes simulation
// /simulations/add/{user_id}/{plant_id}, creates a simulation under that user id with the plant id
// /account/darkMode/{userId}/{darkMode}, updates user's darkmode preference
// /account/guy/{userId}/{guyPreference}, updates guy preference
// /account/pull_preference/darkMode/{userId}, returns preference for user of darkmode
// /account/pull_preference/guy/{userId}, returns preference for user of guy
// all APIs return 500 if there is an internal server error
// MySQL has no password, account accordingly
//

const express = require('express');
const http = require('http');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const path = require('path');
const connectDB = require("./config/db");
const loginRoute = require("./route/loginSignupRoute");
const cookieParser = require("cookie-parser");
const cors = require('cors');
require("dotenv").config();

const app = express();
const port = 9100;
const localNetworkHost = '0.0.0.0';

// CORS setup (must come before routes)
app.use(cors({
  origin: "http://localhost:3000",
  credentials: true,
}));

// Middleware
app.use(express.json());
app.use(bodyParser.json());
app.use(cookieParser());

// MySQL connection
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

// MongoDB connection (if you're using it)
connectDB();

// Routes
app.use("/", loginRoute);

// Static file serving (if needed)
app.use(express.static(path.join(__dirname, '../app')));

// Sample GET route
app.get('/test', (req, res) => {
  connection.query('SELECT * FROM ballots', (err, results) => {
    if (err) {
      console.error('Error fetching ballots:', err);
      res.status(500).send('Server error');
      return;
    }
    res.json(results);
  });
});

// Example POST route
app.post('/envelopeData', (req, res) => {
  const { IMB, DATE, TIME, LOCATION, OCR } = req.body;

  connection.query(
    'INSERT INTO ballots (barcode_data, date, time, location, name) VALUES (?, ?, ?, ?, ?)',
    [IMB, DATE, TIME, LOCATION, OCR],
    (err, results) => {
      if (err) {
        console.error('Error pushing ballot data:', err);
        res.status(500).send('Server error');
        return;
      }
      res.status(200).send("Ballot data saved.");
    }
  );
});

// Optional dummy POST route
app.post('/', (req, res) => {
  res.send('Got a POST request');
});

// Start the server
app.listen(port, localNetworkHost, () => {
  console.log(`Server running at http://${localNetworkHost}:${port}`);
});
