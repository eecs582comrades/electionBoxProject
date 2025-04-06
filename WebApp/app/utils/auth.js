// Name(s): William Johnson
//5/5/25
import { backendUrl } from "@/utils/constant";
const isLoggedIn = async function(){
    const authResponse = await fetch(`${backendUrl}verify`, {
        method: "GET",
        credentials: "include",
    });
    console.log("Logged In:", authResponse.ok);
    return authResponse.ok;
}

export { isLoggedIn }