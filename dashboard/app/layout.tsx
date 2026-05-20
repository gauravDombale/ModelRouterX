import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ModelRouterX",
  description: "Self-hosted LLM gateway dashboard"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

