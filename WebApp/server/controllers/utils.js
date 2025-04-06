// Name(s): William Johnson, Katie Golder
//5/5/25
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// generating access and refresh token
const jwt = require("jsonwebtoken");
const createAccessToken = (email) => {
  const token = jwt.sign(email, process.env.ACCESS_TOKEN_SIGNATURE, {
    expiresIn: "15m",
    algorithm: "HS256",
    issuer: "katie golder",
  });

  return token;
};
const createRefreshToken = (email) => {
  const token = jwt.sign(email, process.env.REFRESH_TOKEN_SIGNATURE, {
    expiresIn: "1d",
    algorithm: "HS256",
    issuer: "katie golder",
  });
  return token;
};

module.exports = { createAccessToken, createRefreshToken };