// Name(s): William Johnson, Katie Golder
//Created: 5/5/25
//Updated: 4/21/25 Logout button only appears on dashboard page

"use client"
import { useEffect, useState } from "react";
import Button from "../button";
import { isLoggedIn } from "@/utils/auth";
import { useRouter, usePathname } from "next/navigation";

const Header: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
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

  const logout = async () => {
    try {
      const res = await fetch("http://localhost:9100/api/logout", {
        method: "POST",
        credentials: "include",
      });

      if (res.ok) {
        console.log("Successfully logged out");
        router.push("/login");
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

//Check logged in and on dashboard page to show logout button (could be changed to one or other if more pages created in future)
  const showLogout = loggedIn && pathname === "/dashboard";

  return (
    <div className="text-center">
      <div className="text-left">
        {showLogout && (
          <Button
            text="Log Out"
            handleButton={logout}
          />
        )}
        {!loggedIn && (
          <Button
            text="Log In"
            handleButton={login}
          />
        )}
      </div>
      <h2 className="capitalize text-2xl font-semibold">Advanced Ballot Drop Box Information</h2>
    </div>
  );
};

export default Header;
