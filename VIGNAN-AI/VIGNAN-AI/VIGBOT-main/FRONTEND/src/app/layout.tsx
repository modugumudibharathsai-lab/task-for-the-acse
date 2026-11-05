import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Geist_Mono } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "VIGNAN-AI | AI-Powered Campus Helpdesk and Grievance Resolution Agent",
  description:
    "Single point of access for authenticated students to personal institutional records, attendance telemetry, examinations, fees, curriculum, and student services.",
  openGraph: {
    title: "VIGNAN-AI",
    description: "AI-Powered Campus Helpdesk and Grievance Resolution Agent for institutional records and services.",
    url: "https://helpdesk.university.edu",
    siteName: "VIGNAN-AI",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "VIGNAN-AI",
    description: "AI-Powered Campus Helpdesk and Grievance Resolution Agent for institutional records and services.",
  },
};

export const viewport = {
  themeColor: "#ffffff",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

import { StudentProvider } from "@/context/StudentContext";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      data-scroll-behavior="smooth"
      className={`h-full ${jakarta.variable} ${geistMono.variable}`}
    >
      <body className="min-h-full flex flex-col antialiased bg-background text-foreground selection:bg-blue-100 selection:text-blue-900">
        <StudentProvider>
          {children}
        </StudentProvider>
      </body>
    </html>
  );
}
