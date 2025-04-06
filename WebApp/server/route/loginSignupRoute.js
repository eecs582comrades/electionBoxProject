// Name(s): William Johnson, Katie Golder
//5/5/25
// https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969
// Login Route
const express = require("express");
const signupController = require("../controllers/signupController");
const loginController = require("../controllers/loginController");
const authUser = require("../middleware/authUser");
const router = express.Router();
// Route to handle user signup requests, uses the signup controller logic
router.post("/signup", signupController);
// Route to handle user login requests, uses the login controller logic
router.post("/login", loginController);
// Route to verify if a user is authenticated, uses the auth middleware to check tokens
router.get("/verify", authUser);

//ChatGPT
// routes/auth.js or wherever your routes are


router.post('/api/logout', (req, res) => {
  res.clearCookie('token', {
    httpOnly: true,
    sameSite: 'Lax', // Use 'None' and secure: true if over HTTPS
    secure: process.env.NODE_ENV === 'production'
  });

  res.status(200).json({ message: "Logged out" });
});

module.exports = router;