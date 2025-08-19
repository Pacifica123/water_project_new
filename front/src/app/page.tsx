// import Image from "next/image";

"use client";
import { useEffect, useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("loading...");
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  // console.log("backendUrl =", process.env.NEXT_PUBLIC_BACKEND_URL);

  useEffect(() => {
    fetch(`/api/hello`)
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(() => setMessage("error"));
  }, []);

  return (
    <main style={{ padding: "2rem" }}>
      <h1>Next.js Frontend</h1>
      <p>Backend says: {message}</p>
    </main>
  );
}
