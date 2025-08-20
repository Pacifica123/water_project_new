// src/app/auth/login/page.tsx : страница авторизации
"use client";
import LoginForm from "../loginForm";

export default function LoginPage() {
  return (
    <main style={{ padding: "2rem" }}>
      <h1>Login</h1>
      <LoginForm />
    </main>
  );
}
