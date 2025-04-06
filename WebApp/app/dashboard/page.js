// Name(s): William Johnson, Katie Golder
//5/5/25
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// dashboard.js which is protected routes and wrapped in HOC
"use client";
import React from "react";
import ProtectedRoutes from "../components/HOC/ProtectedRoutes";

const Page = () => {

  const tryLogout = function(){
    alert("Oh Noe!");
  }

  return (
    <div className="text-center">
      <h2 className="capitalize text-2xl font-semibold">This is dashboard.</h2>
      <p>😊 You have been successfully logged in.</p>
    </div>
  );
};

export default ProtectedRoutes(Page);