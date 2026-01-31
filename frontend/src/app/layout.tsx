import type { Metadata } from "next";
import { Geist, Geist_Mono, Oswald } from "next/font/google";
import "./globals.css";
import { Sidebar, MobileNav } from "@/components/Sidebar";
import { Toaster } from "@/components/ui/sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const oswald = Oswald({
  variable: "--font-oswald",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ragebAIt | Your Brutal AI Coach",
  description: "Get roasted by AI for your sports form.",
};

import { SessionProvider } from "@/lib/session-context";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark h-full">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${oswald.variable} antialiased h-full bg-background text-foreground`}
      >
        <SessionProvider>
          <div className="flex h-full min-h-screen relative">
            {/* Desktop Sidebar */}
            <div className="hidden md:flex w-72 flex-col fixed inset-y-0 z-50 border-r border-sidebar-border bg-sidebar">
              <Sidebar />
            </div>

            {/* Main Content */}
            <div className="flex-1 md:pl-72 flex flex-col h-full w-full">
              {/* Mobile Header/Nav */}
              <MobileNav />

              {/* Page Content */}
              <main className="flex-1 relative overflow-y-auto">
                {children}
              </main>
            </div>
          </div>
          <Toaster />
        </SessionProvider>
      </body>
    </html>
  );
}
