// Name(s): William Johnson, Katie Golder
//5/5/25
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// dashboard.js which is protected routes and wrapped in HOC
"use client";
import { useEffect, useState } from "react";
import { BallotTable } from "../components/ballotTable";
import React from "react";
import ProtectedRoutes from "../components/HOC/ProtectedRoutes";


const Page = () => {

  //Gets Ballot table data
  const [data, setData] = useState(null);
    function filterResults(rawData){
    }
    useEffect(() => {
      fetch("http://localhost:9100/test") // Replace with your backend API
        .then((res) => res.json())
        .then((data) => setData(data))
        .catch((error) => console.error("Error fetching data:", error));
    }, []);

  //User not logged in
  const tryLogout = function(){
    alert("Oh no! An login error occured.");
  }

  return (
    <div className="text-center">
      <p>Welcome Douglas County Election Official</p>
      <br></br>
      <div className="font-medium text-black-500"><BallotTable data={data}/></div>
    </div>
  );
};

export default ProtectedRoutes(Page);