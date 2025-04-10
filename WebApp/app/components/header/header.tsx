// Name(s): William Johnson, Katie Golder
//5/5/25

"use client"
import { useEffect, useState } from "react";
import Button from "../button";
import { isLoggedIn } from "@/utils/auth";
import { useRouter } from "next/navigation";

const Header: React.FC = () => {
  const router = useRouter();
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null); // State to track login status

  useEffect(() => {
    const checkLogin = async () => {
      const result = await isLoggedIn();
      setLoggedIn(result); // Update state
    };
    checkLogin();
  }, []);
  
  const login = () => {
    router.push("/login"); // Redirect to the login page
  };

  //ChatGPT
  const logout = async () => {
    try {
      const res = await fetch("http://localhost:9100/api/logout", {
        method: "POST",
        credentials: "include", // Important: sends the cookie
      });
  
      if (res.ok) {
        console.log("Successfully logged out");
        router.push("/login"); // Or update state to logged out
      } else {
        console.error("Logout failed");
      }
    } catch (error) {
      console.error("Logout error:", error);
    }
  };
  
  

  if (loggedIn === null) {
    return <div>Pending Login...</div>; // Render loading until login check completes
  }

  return (
    <div className="text-center">
      <div className="text-left">
        <Button
          text={loggedIn ? "Log Out" : "Log In"}
          handleButton={loggedIn ? logout : login}
        />
      </div>
      <h2 className="capitalize text-2xl font-semibold">Advanced Ballot Drop Box Information</h2>
    </div>
  );
};

export default Header;
