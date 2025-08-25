// src/app/api/client.ts : обёртка fetch + базовый URL
const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    mode: "cors",
    credentials: "include", // если нужны куки
    headers: {
      // "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  return res.json();
}
