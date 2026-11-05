"use client";

import React from "react";
import Image from "next/image";
import { ArrowRight, ShieldCheck, Lock } from "lucide-react";
import { ThreeAiCore } from "./ThreeAiCore";

interface LandingPageProps {
  onGetStarted: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted }) => {
  return (
    <div className="min-h-dvh flex flex-col justify-between bg-card text-foreground selection:bg-blue-100 selection:text-blue-900 font-sans">
      {/* 1. MINIMAL INSTITUTIONAL NAVIGATION BAR */}
      <nav className="w-full border-b border-slate-200/80 bg-card/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 py-3.5">
          {/* Vignan Institutional & VIGNAN-AI Branding */}
          <div className="flex items-center gap-3">
            <Image
              src="/vignan-logo.png"
              alt="Vignan Foundation"
              width={140}
              height={44}
              priority
              className="h-9 sm:h-11 w-auto object-contain"
            />
            <div className="h-6 w-px bg-slate-200 hidden sm:block" />
            <div className="hidden sm:block">
              <span className="text-sm font-bold tracking-tight text-foreground leading-tight block">
                VIGNAN-AI
              </span>
              <p className="text-[11px] text-muted-foreground leading-none mt-0.5">
                Autonomous University System
              </p>
            </div>
          </div>

          {/* Primary Student Login Action */}
          <div className="flex items-center gap-3">
            <button
              onClick={onGetStarted}
              className="flex items-center gap-1.5 rounded-full bg-blue-600 px-4 sm:px-5 py-2 text-xs sm:text-sm font-semibold text-white shadow-xs hover:bg-blue-700 transition-all cursor-pointer"
            >
              <span>Student Login</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </nav>

      {/* 2. MINIMAL HERO SECTION */}
      <main className="relative flex-1 flex items-center justify-center overflow-hidden py-12 sm:py-16 lg:py-20">
        {/* Subtle Background Radial Grid */}
        <div className="absolute inset-0 pointer-events-none opacity-25">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: "radial-gradient(#93c5fd 1px, transparent 1px)",
              backgroundSize: "32px 32px",
            }}
          />
        </div>

        <div className="relative mx-auto grid max-w-7xl grid-cols-1 items-center gap-10 px-4 sm:px-6 lg:grid-cols-[1.1fr_0.9fr] w-full">
          {/* Left Column: Heading, Description & Primary CTA */}
          <div className="max-w-2xl space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 border border-blue-200">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Official Institutional Student Portal</span>
            </div>

            <h1 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-5xl lg:text-6xl leading-[1.15]">
              Your Campus. <br />
              <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 bg-clip-text text-transparent">
                Connected by Intelligence.
              </span>
            </h1>

            <p className="text-base sm:text-lg leading-relaxed text-muted-foreground">
              Experience a smarter campus with VIGNAN-AI – your intelligent assistant for academic
              information, student support, campus services and grievance resolution.
            </p>

            {/* Primary Action Button */}
            <div className="pt-2 flex flex-wrap items-center gap-4">
              <button
                onClick={onGetStarted}
                className="flex items-center gap-2 rounded-full bg-blue-600 px-7 py-3.5 text-sm sm:text-base font-semibold text-white shadow-lg shadow-blue-600/25 hover:bg-blue-700 hover:shadow-blue-600/35 transition-all cursor-pointer"
              >
                <span>Student Login</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>

            {/* Security Guarantee Note */}
            <div className="pt-4 flex items-center gap-2 text-xs text-muted-foreground border-t border-slate-100">
              <Lock className="h-3.5 w-3.5 text-indigo-600" />
              <span>Access restricted to enrolled VFSTR students with verified credentials.</span>
            </div>
          </div>

          {/* Right Column: Animated Three.js 3D AI Visual */}
          <div className="relative flex items-center justify-center">
            <div className="relative w-full rounded-2xl border border-slate-200/80 bg-gradient-to-b from-blue-50/40 via-white to-slate-50/60 p-2 shadow-xl shadow-slate-200/50">
              <ThreeAiCore />
              <div className="text-center pb-2 text-[11px] text-muted-foreground flex items-center justify-center gap-1.5">
                <span className="inline-block h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                <span>Interactive 3D AI Core • Drag to Rotate</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 3. MINIMAL INSTITUTIONAL FOOTER */}
      <footer className="w-full border-t border-slate-200/80 bg-card py-6">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-muted-foreground">
          <p>© {new Date().getFullYear()} Vignan Foundation for Science, Technology and Research (VFSTR). All rights reserved.</p>
          <div className="flex items-center gap-4">
            <button
              onClick={onGetStarted}
              className="hover:text-blue-600 transition-colors cursor-pointer"
            >
              Student Portal
            </button>
            <span>•</span>
            <a
              href="/admin/login"
              className="hover:text-blue-600 transition-colors"
            >
              Nodal Officer / Admin Login
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};
