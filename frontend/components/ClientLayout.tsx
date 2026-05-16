"use client";

import { ThemeProvider } from "./ThemeProvider";
import SplashScreen from "./SplashScreen";
import Sidebar from "./Sidebar";

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ThemeProvider>
      <SplashScreen />
      <div className="flex h-screen overflow-hidden bg-[var(--bg)] text-[var(--text)] transition-colors duration-300">
        {/* Sidebar */}
        <Sidebar />
        
        {/* Main content */}
        <main className="flex-1 overflow-y-auto bg-gradient-to-br from-[var(--bg)] to-[var(--bg-secondary)]">
          <div className="container mx-auto p-6 max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </ThemeProvider>
  );
}

// Made with Bob
