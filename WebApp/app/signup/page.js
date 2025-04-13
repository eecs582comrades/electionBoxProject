//DO NOT KEEEEEEEEEEEEEEEEEEEEEP XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Name(s): William Johnson, Katie Golderm Emily Tso
//5/5/25
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// signup page
"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import LoginInput from "../components/loginInput";
import { backendUrl } from "../utils/constant";
import Button from "../components/button";

const Page = () => {
  const router = useRouter();
  // handling the input
  const handleInput = (e) => {
    setSignupData({ ...signupData, [`${e.target.name}`]: e.target.value });
  };
  // storing the value of the sign up
  const [signupData, setSignupData] = useState({
    email: "",
    password: "",
  });
  // handling the signup button when presses
  const handleSignup = async (e) => {
    e.preventDefault();
    // handling the email and password when the length of both of them is 0
    if (signupData.email.length === 0 || signupData.password.length === 0) {
      alert("Please fill the form");
      return null;
    }
    try {
      const response = await fetch(`${backendUrl}signup`, {
        method: "POST",
        body: JSON.stringify(signupData),
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        // just to show that login is done message
        setInterval(() => {
          router.push("/login");
        }, 2000);
      }

      if (response.statusText === "Conflict") {
        alert("user already exist");
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div
      className="flex   
 items-center justify-center h-screen relative w-full"
    >
      <div className="absolute top-5 left-5">
        <Button text="Login" link="/login" shadowColor={"yellow"} />
      </div>
       
      <div className="bg-white dark:bg-gray-900 p-8 rounded-lg shadow-2xl w-[25rem] border-2 border-solid border-black dark:border-gray-700">
        <form className="space-y-4">
          <LoginInput
            label={"Email:"}
            handleInput={handleInput}
            type="email"
            value={signupData.email}
          />
          <LoginInput
            label="Password:"
            handleInput={handleInput}
            type={"password"}
            value={signupData.password}
          />
          <Button text="sign up" handleButton={handleSignup} />
        </form>
      </div>
    </div>
  );
};

export default Page;