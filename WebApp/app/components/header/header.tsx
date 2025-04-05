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

  const logout = () => {
    alert("Logging out...");
    // You can add logout logic here (e.g., clearing session, tokens)
  };

  if (loggedIn === null) {
    return <div>Loading Dog...</div>; // Render loading until login check completes
  }

  return (
    <Button
      text={loggedIn ? "Log Out" : "Log In"}
      handleButton={loggedIn ? logout : login}
    />
  );
};

export default Header;
