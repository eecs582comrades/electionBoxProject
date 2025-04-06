// Name(s): William Johnson, Katie Golder
//5/5/25
//https://nextjs.org/docs/pages/building-your-application/authentication
const mongoose = require("mongoose");

async function connectDB() {
  try {
    await mongoose.connect("mongodb://localhost:27017/user", {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log("MongoDB connected");
  } catch (err) {
    console.error("MongoDB connection error:", err);
    process.exit(1); // Exit the app if connection fails
  }
}

module.exports = connectDB;
