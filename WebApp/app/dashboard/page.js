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