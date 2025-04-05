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

module.exports = router;