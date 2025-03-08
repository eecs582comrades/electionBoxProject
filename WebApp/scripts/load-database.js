// Name of code artifact: All of them
// Description: Node.js setup script for configuring the local database
// Name(s): William Johnson, Katie Golder
// Date Created: 10-25-24
// Dates Revised: 12-2-24
// Brief description of each revision & author: Katie added plant image support on 12-2-24

const { spawn } = require('child_process');
const path = require('path');

// Replace backslashes with forward slashes for Windows compatibility
const user = 'root';
const password = '';
const host = 'localhost';
const database = 'electionbox';
let sqlFile = path.join(__dirname, '..', 'database', 'initial_database.sql').replace(/\\/g, '/'); // Ensure slashes

// Command options
const args = [
  '--binary-mode=1',
  `-u${user}`,
  `-p${password}`,
  `-h${host}`,
  `${database}`
];

console.log("Initializing Database Structures...");
// Spawn the MySQL process
const mysql = spawn('mysql', args, {
  stdio: ['pipe', process.stdout, process.stderr] // Use stdio to handle redirection
});

// Use file redirection in a cross-platform way
const fs = require('fs');
const fileStream = fs.createReadStream(sqlFile);

// Pipe the SQL file to MySQL's stdin
fileStream.pipe(mysql.stdin);

mysql.on('close', (code) => {
  if (code === 0) {
    console.log('Database loaded successfully.');
  } else {
    console.error(`Database loading process exited with code ${code}`);
  }
});

async function load_data() {
  try {
    // Read JSON data from file
    const jsonData = JSON.parse(fs.readFileSync('./artifacts/testdata.json', 'utf8'));
    
    // Iterate through each plant record
    for (const ballot of jsonData) {
      const ballotId = ballot["ballot_id"];
      const barcodeData = ballot["barcode_data"];
      const name = ballot["name"];
      const date = ballot["date"];
      const time = ballot["time"]
      const location = ballot["location"];
     

      // SQL to check if the plant already exists
      const checkSQL = `SELECT COUNT(*) AS count FROM ballots WHERE ballot_id = '${ballotId}';`;

      // Execute the SQL command to check if the plant exists
      const checkProcess = spawn('mysql', [...args, '-e', checkSQL]);

      let checkResult = '';
      for await (const chunk of checkProcess.stdout) {
        checkResult += chunk;
      }

      checkProcess.on('close', async (code) => {
        if (code !== 0) {
          console.error(`Failed to check existence for ballot ${ballotId}`);
          return;
        }

        // Parse the result to get the count
        const count = parseInt(checkResult.match(/\d+/)[0], 10);

        if (count === 0) {
          // SQL to insert the plant if it doesn't exist
          const insertSQL = `
            INSERT INTO ballots (
              ballot_id,
              barcode_data,
              name,
              date,
              time,
              location
            ) VALUES (
              '${ballotId}',
              '${barcodeData.replace(/'/g, "''")}',
              '${name.replace(/'/g, "''")}',
              '${date.replace(/'/g, "''")}',
              '${time}',
              '${location.replace(/'/g, "''")}'
            );
          `;

          // Execute the insert command
          const insertProcess = spawn('mysql', [...args, '-e', insertSQL]);

          insertProcess.on('close', (insertCode) => {
            if (insertCode === 0) {
              console.log(`Inserted new ballot: ${ballotId}`);
            } else {
              console.error(`Failed to insert ballot: ${ballotId}`);
            }
          });
        } else {
          console.log(`Ballot ${ballotId} already exists, skipping.`);
        }
      });
    }

    console.log('Data loading complete.');
  } catch (err) {
    console.error('Error loading ballot data:', err);
  }
}


load_data();