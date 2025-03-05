"use client";
import { useEffect, useState } from "react";

export default function MyComponent() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5100/test") // Replace with your backend API
      .then((res) => res.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  return <div>{data ? JSON.stringify(data) : "Loading..."}</div>;
}