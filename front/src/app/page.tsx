// import Image from "next/image";

"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.push("/auth/login");
  }, [router]);
  return null;
}

// testing routers:

// export default function Home() {
//   const [message, setMessage] = useState("loading...");
//   const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
//   // console.log("backendUrl =", process.env.NEXT_PUBLIC_BACKEND_URL);

//   useEffect(() => {
//     fetch(`/api/v1/hello`)
//       .then(res => res.json())
//       .then(data => setMessage(data.message))
//       .catch(() => setMessage("error"));
//   }, []);

//   return (
//     <main style={{ padding: "2rem" }}>
//       <h1>Next.js Frontend</h1>
//       <p>Backend says: {message}</p>
//     </main>
//   );
// }
