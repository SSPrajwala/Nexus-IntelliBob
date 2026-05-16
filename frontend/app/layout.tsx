import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import ClientLayout from "@/components/ClientLayout";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Nexus-IntelliBob | AI Incident Intelligence Platform",
  description: "Enterprise AI platform for predicting and preventing system failures. Analyzing Systems. Predicting Failures.",
  keywords: ["AI", "Incident Intelligence", "System Reliability", "Failure Prediction", "DevOps"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="antialiased font-sans">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}

// Made with Bob
