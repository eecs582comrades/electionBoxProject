// Name(s): William Johnson, Katie Golder
//5/5/25
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// authUser.js
const jwt = require("jsonwebtoken");
const { createAccessToken } = require("../controllers/utils");

const authUser = (req, res) => {
  console.log(req.cookies);
  const accessToken = req.cookies["accessToken"];
  const refreshToken = req.cookies["refreshToken"];

  //   checking if both token are not available
  if (!accessToken && !refreshToken) {
    return res.status(401).send("Access Denied. No token provided");
  }
  try {
    const decodeAccessToken = jwt.verify(
      accessToken,
      process.env.ACCESS_TOKEN_SIGNATURE
    );
    console.log("Access Token:", decodeAccessToken);
    return res.status(200).send("Hello Potato");
  } catch (err) {
    if (!accessToken) {
      console.log("No access token provided");
    }
    try {
      const decodeRefreshToken = jwt.verify(
        refreshToken,
        process.env.REFRESH_TOKEN_SIGNATURE
      );

      const { email } = decodeRefreshToken;

      const accessToken = createAccessToken({ email });

      res.cookie("accessToken", accessToken, {
        secure: false,

        httpOnly: true,
        sameSite: "", // Helps prevent CSRF attacks
        // making it valid for 15 min
        expires: new Date(Date.now() + 15 * 60 * 1000), //
      });
      res.json({
        message: "User Verifies",
        email: email,
        conditon: "Access Token Refresh",
      });
    } catch (err) {
      console.log(err);
    }
  }
};

module.exports = authUser;