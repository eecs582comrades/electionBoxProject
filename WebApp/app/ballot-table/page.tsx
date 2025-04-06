// Name(s): William Johnson, Katie Golder

"use client";
import { useEffect, useState } from "react";
import { BallotTable } from "../components/ballotTable";

export default function MyComponent() {
  const [data, setData] = useState(null);


  function filterResults(rawData){

  }

  useEffect(() => {
    fetch("http://localhost:9100/test") // Replace with your backend API
      .then((res) => res.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  return (
    <div id="contentArea">
        <div className="flex flex-col gap-2 p-8 sm:flex-row sm:items-center sm:gap-6 sm:py-4 ...">
          <div className="space-y-2 text-center sm:text-left">
            <div className="space-y-0.5">
              <p className="text-lg font-semibold text-black">Hello Election Official</p>
              <div className="font-medium text-black-500"><BallotTable data={data}/></div>
            </div>
          </div>
      </div>
    </div>
    
  );

  
}
