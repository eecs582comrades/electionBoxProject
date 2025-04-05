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

const express = require('express')
const http = require('http');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const path = require('path');
const connectDB = require("./config/db");
const loginRoute = require("./route/loginSignupRoute");
const cookieParser = require("cookie-parser");
require("dotenv").config();

const cors = require('cors');

// this has been used so to allow the server side to put the cookie in the frontend site. You should use the port number that has been used in frontend.
const corsOptions = {
  origin: "http://localhost:3000",
  credentials: true, // Allow credentials
};


const app = express();
app.use(cors(corsOptions));
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

app.use(express.json());
connectDB();
// cookie parser is used for handling the cookies
app.use(cookieParser());

app.use("/", loginRoute);



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
})

app.post('/', (req, res) => {
    res.send('Got a POST request')
})

// Registers the app to use bodyParser to make our lives easier and avoid needing to decode json frequently.
app.use(bodyParser.json());