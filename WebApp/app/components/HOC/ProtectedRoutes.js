//Wil Johnson, Katie Golder
//5/5/25
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// ProtectedRoutes.js
import { isLoggedIn } from "../../utils/auth";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const ProtectedRoutes = (WrapperComponent) => {
  const AuthWrapper = (props) => {
    const router = useRouter();
    const [isAuthChecked, setIsAuthChecked] = useState(false); // To track when auth check completes

    useEffect(() => {
      const checkAuth = async () => {
        try {
          const loggedIn = await isLoggedIn();
          if (!loggedIn) {
            router.push("/login");
          }
        } catch (err) {
          router.push("/login");
        } finally {
          setIsAuthChecked(true); // Set to true once the check is done
        }
      };

      if (!isAuthChecked) {
        checkAuth(); // Only check if auth isn't checked yet
      }
    }, [isAuthChecked, router]);





    // Only render the WrapperComponent once authentication is checked
    if (!isAuthChecked) {
      return <div>Loading Cat...</div>; // Or nothing, or a spinner
    }

    return <WrapperComponent {...props} />;
  };

  return AuthWrapper;
};

export default ProtectedRoutes;
