// Name(s): William Johnson, Katie Golder
//Created: 5/5/25
//Updated: 5/21/25 with CSV downloading and from js file to tsx;
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// dashboard.js
"use client";
import { useEffect, useState } from "react";
import { BallotTable } from "../components/ballotTable";
import React from "react";
import ProtectedRoutes from "../components/HOC/ProtectedRoutes";

const Page = () => {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://localhost:9100/test")
      .then((res) => res.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  // CSV download handler ChatGPT 5/21/25
  const downloadCSV = () => {
    if (!data || data.length === 0) {
      alert("No data to download!");
      return;
    }

    const csvRows = [];

    // Get headers
    const headers = Object.keys(data[0]);
    csvRows.push(headers.join(","));

    // Get row values
    for (const row of data) {
      const values = headers.map(header => {
        const val = row[header];
        return `"${val !== null && val !== undefined ? val : ""}"`;
      });
      csvRows.push(values.join(","));
    }

    const csvData = csvRows.join("\n");
    const blob = new Blob([csvData], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "ballot_data.csv";
    a.click();

    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="text-center">
      <p>Welcome</p>
      <br />
      <button
        onClick={downloadCSV}
        className="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded mb-4"
      >
        Download CSV
      </button>
      <div className="font-medium text-black-500">
        <BallotTable data={data} />
      </div>
    </div>
  );
};

export default ProtectedRoutes(Page);
