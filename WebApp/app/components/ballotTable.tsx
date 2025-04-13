//Format ballot data into table
// Name(s): William Johnson, Katie Golder, Emily Tso 

"use client";

export default function BallotTable({ data }) {
  console.log(data);
  return (
    <div id="contentArea">
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th className="border border-black dark:border-white px-4 py-2">BallotID</th>
            <th className="border border-black dark:border-white px-4 py-2">Date</th>
            <th className="border border-black dark:border-white px-4 py-2">Time</th>
            <th className="border border-black dark:border-white px-4 py-2">Location</th>
            <th className="border border-black dark:border-white px-4 py-2">Barcode Data</th>
          </tr>
        </thead>
        <tbody>
          {data ? data.map((ballot, index) => (
            <tr key={index}>
              <td className="border border-black dark:border-white px-4 py-2">{ballot.ballot_id}</td>
              <td className="border border-black dark:border-white px-4 py-2">{ballot.date}</td>
              <td className="border border-black dark:border-white px-4 py-2">{ballot.time}</td>
              <td className="border border-black dark:border-white px-4 py-2">{ballot.location}</td>
              <td className="border border-black dark:border-white px-4 py-2">{ballot.barcode_data}</td>
            </tr>
          )) : (<tr/>)}
        </tbody>
      </table>
    </div>
  );
}

export { BallotTable };
