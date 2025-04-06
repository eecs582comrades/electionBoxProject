//Wil Johnson, Katie Golder
//5/5/25
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// signup controller
const User = require("../models/userModel");
const bcrypt = require("bcryptjs");
const signupController = async (req, res, next) => {
// accessing email and password 
  const { email, password } = req.body;
  const salt = await bcrypt.genSaltSync(10);
// hashing password using bcrypt
  const hashedPassword = await bcrypt.hash(password, salt);

  const newUser = new User({
    email: email,
    password: hashedPassword,
  });
  newUser
    .save()
    .then((success) => {
      return res.status(200).json({ message: "User has been saved" });
    })
    .catch((err) => {
      if (err === 11000) {
        console.log("dublicate");
        return res.status(409).json({ message: "User Already Detected" });
      }
      console.log(err);
    });
};

module.exports = signupController;