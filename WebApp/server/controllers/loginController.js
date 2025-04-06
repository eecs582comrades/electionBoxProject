//Wil Johnson, Katie Golder
//5/5/25
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// loginController.js
const UserModal = require("../models/userModel");
const bcrypt = require("bcryptjs");
const { createAccessToken, createRefreshToken } = require("./utils");

const loginController = (req, res, next) => {
  console.log(req.body);
  const user = req.body;
  const { email, password } = req.body;

  UserModal.findOne({ email }).then((data) => {
    if (data) {
      const storedPassword = data.password;
      bcrypt.compare(password, storedPassword, (err, result) => {
        if (err) {
          console.log(err);
        }
        console.log(result);
        if (result) {
          const accessToken = createAccessToken({ email });
          const refreshToken = createRefreshToken({ email });
          // sending the refresh token
          res.cookie("refreshToken", refreshToken, {
            httpOnly: true,
            secure: false,
            sameSite: "",
            expires: new Date(Date.now() + 60 * 60 * 60 * 24 * 1 * 1000),
          });
          // sending the access token
          res.cookie("accessToken", accessToken, {
            secure: false,

            httpOnly: true,
            sameSite: "", // Helps prevent CSRF attacks
            // making it valid for 15 min
            expires: new Date(Date.now() + 15 * 60 * 1000), //
          });

          res.json({
            success: true,
            message: "Authentication Successfull",
          });
        }
      });
    }
  });

  const accessToken = createAccessToken(user);
};

module.exports = loginController;