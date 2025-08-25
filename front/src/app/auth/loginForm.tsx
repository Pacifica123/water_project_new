// src/app/auth/loginForm.tsx : форма для входа
"use client";
import { useState } from "react";
import { apiFetch } from "../api/client";

export default function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError("");

const formData = JSON.stringify({
  username,
  password
});

  try {
    const res = await apiFetch("/api/v1/auth/login", {
      method: "POST",
      body: formData,
      headers: {
        "Content-Type": "application/json"
      }
    });
    console.log("Logged in:", res);
  } catch (err: any) {
    setError(err.message);
  }
};


  return (
    <form onSubmit={handleSubmit}>
      <input
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      <button type="submit">Login</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
}
