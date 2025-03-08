//Format ballot data into table
"use client";

export default function BallotTable({ data }) {
  console.log(data);
  return (
    <div id="contentArea">
    <table style={{ borderCollapse: 'collapse', width: '100%' }}>
      <thead>
        <tr>
          <th style={{ border: '1px solid black', padding: '8px' }}>BallotID</th>
          <th style={{ border: '1px solid black', padding: '8px' }}>Date</th>
          <th style={{ border: '1px solid black', padding: '8px' }}>Time</th>
          <th style={{ border: '1px solid black', padding: '8px' }}>Location</th>
          <th style={{ border: '1px solid black', padding: '8px' }}>Barcode Data</th>
        </tr>
      </thead>
      <tbody>
        { data ? data.map((ballot, index) => (
          <tr key={index}>
            <td style={{ border: '1px solid black', padding: '8px' }}>{ballot.ballot_id}</td>
            <td style={{ border: '1px solid black', padding: '8px' }}>{ballot.date}</td>
            <td style={{ border: '1px solid black', padding: '8px' }}>{ballot.time}</td>
            <td style={{ border: '1px solid black', padding: '8px' }}>{ballot.location}</td>
            <td style={{ border: '1px solid black', padding: '8px' }}>{ballot.barcode_data}</td>
          </tr>
        )) : (<tr/>)}
      </tbody>
    </table>
    </div>
  );

  
}

export { BallotTable };