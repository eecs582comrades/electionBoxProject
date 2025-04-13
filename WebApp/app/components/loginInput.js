// Name(s): William Johnson, Katie Golder, Emily Tso
//5/5/25
//https://medium.com/@neupanesahitya1/how-to-implement-jwt-authentication-with-next-js-and-express-from-signup-to-secure-routes-226351bc1969

// LoginInput.js

import React from "react";

const LoginInput = ({ label, handleInput, type, value }) => {
  return (
    <div className="flex flex-col">
      <label className="text-gray-700 dark:text-white">{label}</label>
      <input
        type={type}
        name={type}
        className="border rounded-md px-3 py-2 text-black dark:text-white"
        onChange={handleInput}
        autoComplete="true"
        value={value}
      />
    </div>
  );
};

export default LoginInput;

