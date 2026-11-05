"use client";

import Image from "next/image";
import React, { useState } from "react";
import {
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Lock,
  User,
  CheckCircle2,
  KeyRound,
  ArrowLeft,
  Mail,
  RefreshCw,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";
import { apiClient } from "@/lib/api-client";
import { useStudent } from "@/context/StudentContext";

interface LoginViewProps {
  onLogin: () => void;
  onBack?: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLogin, onBack }) => {
  const { t } = useLanguage();
  const { loginAsStudent, activateAndLoginStudent } = useStudent();

  // Mode: 'login' | 'activate' | 'reset'
  const [authMode, setAuthMode] = useState<"login" | "activate" | "reset">("login");

  // Sign In State (starts completely clean, no prefilled accounts)
  const [studentId, setStudentId] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Activation & Reset State
  const [regdNo, setRegdNo] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [maskedEmail, setMaskedEmail] = useState<string | null>(null);
  const [otpCode, setOtpCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const resetMessages = () => {
    setError(null);
    setSuccessMsg(null);
  };

  // 1. Existing Student Sign In
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();

    const regd = studentId.trim().toUpperCase();
    if (!regd) {
      setError("Please enter your Student Registration Number.");
      return;
    }
    if (!password.trim()) {
      setError("Please enter your password.");
      return;
    }

    setIsLoading(true);
    try {
      await loginAsStudent(regd, password.trim());
      setIsLoading(false);
      onLogin();
    } catch (err: any) {
      setIsLoading(false);
      setError(err?.message || "Invalid registration number or password.");
    }
  };

  // 2. Request OTP for First-Time Account Activation
  const handleRequestActivationOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();

    const cleanRoll = regdNo.trim().toUpperCase();
    if (!cleanRoll) {
      setError("Please enter your Student Registration Number.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await apiClient.requestActivationOtp(cleanRoll);
      setIsLoading(false);
      if (res.requires_admin_verification) {
        setError(res.message);
        return;
      }
      setOtpSent(true);
      setMaskedEmail(res.masked_email || null);
      setSuccessMsg(res.message || "A 6-digit verification code has been dispatched to your institutional email.");
    } catch (err: any) {
      setIsLoading(false);
      setError(err?.message || "Could not request verification code. Please check your registration number.");
    }
  };

  // 3. Verify OTP and Activate Account
  const handleVerifyAndActivate = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();

    const cleanRoll = regdNo.trim().toUpperCase();
    if (!otpCode.trim() || otpCode.trim().length !== 6) {
      setError("Please enter the 6-digit verification code sent to your email.");
      return;
    }
    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (!/[A-Za-z]/.test(newPassword) || !/[0-9]/.test(newPassword)) {
      setError("Password must contain at least one letter and one number.");
      return;
    }
    if (newPassword.trim().toUpperCase() === cleanRoll) {
      setError("Password cannot be your registration number.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);
    try {
      await activateAndLoginStudent(cleanRoll, otpCode.trim(), newPassword, confirmPassword);
      setIsLoading(false);
      onLogin();
    } catch (err: any) {
      setIsLoading(false);
      setError(err?.message || "Account activation failed. Please check your verification code.");
    }
  };

  // 4. Request Password Reset OTP
  const handleRequestResetOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();

    const cleanRoll = regdNo.trim().toUpperCase();
    if (!cleanRoll) {
      setError("Please enter your Student Registration Number.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await apiClient.requestPasswordResetOtp(cleanRoll);
      setIsLoading(false);
      setOtpSent(true);
      setMaskedEmail(res.masked_email || null);
      setSuccessMsg(res.message || "Password reset verification code dispatched.");
    } catch (err: any) {
      setIsLoading(false);
      setError(err?.message || "Could not request reset code. Please check your registration number.");
    }
  };

  // 5. Verify OTP and Reset Password
  const handleVerifyAndReset = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();

    const cleanRoll = regdNo.trim().toUpperCase();
    if (!otpCode.trim() || otpCode.trim().length !== 6) {
      setError("Please enter the 6-digit verification code sent to your email.");
      return;
    }
    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (!/[A-Za-z]/.test(newPassword) || !/[0-9]/.test(newPassword)) {
      setError("Password must contain at least one letter and one number.");
      return;
    }
    if (newPassword.trim().toUpperCase() === cleanRoll) {
      setError("Password cannot be your registration number.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await apiClient.verifyAndResetPassword(cleanRoll, otpCode.trim(), newPassword, confirmPassword);
      setIsLoading(false);
      setSuccessMsg(res.message || "Password reset successfully. You can now sign in.");
      setStudentId(cleanRoll);
      setPassword(newPassword);
      setAuthMode("login");
      setOtpSent(false);
      setOtpCode("");
    } catch (err: any) {
      setIsLoading(false);
      setError(err?.message || "Password reset verification failed.");
    }
  };

  return (
    <div className="min-h-dvh w-full flex flex-col justify-between bg-muted/40 text-foreground relative overflow-hidden font-sans">
      {/* Ambient background decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div
          className="absolute inset-0 opacity-[0.3]"
          style={{
            backgroundImage: "radial-gradient(#93c5fd 1px, transparent 1px)",
            backgroundSize: "32px 32px",
          }}
        />
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-blue-100/40 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Top Header */}
      <header className="relative z-10 w-full border-b border-slate-200/80 bg-card/90 backdrop-blur-md px-4 sm:px-6 py-3.5">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
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
              <span className="text-sm font-bold tracking-tight text-foreground block">
                VIGNAN-AI
              </span>
              <p className="text-[11px] text-muted-foreground leading-none mt-0.5">
                Autonomous University System
              </p>
            </div>
          </div>
          {onBack && (
            <button
              onClick={onBack}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-slate-200 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-card transition-colors cursor-pointer"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Back to Home</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Authentication Card */}
      <main className="relative z-10 flex-1 flex items-center justify-center p-4 sm:p-6 my-auto">
        <div className="w-full max-w-md">
          <div className="rounded-2xl border border-slate-200 bg-card/95 backdrop-blur-xl p-6 sm:p-8 shadow-xl shadow-slate-200/50 space-y-5">
            {/* Header Badge & Title */}
            <div className="text-center space-y-1.5">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold tracking-wide">
                <ShieldCheck className="h-3.5 w-3.5" />
                <span>
                  {authMode === "login"
                    ? "Verified Student Sign In"
                    : authMode === "activate"
                    ? "First-Time Account Activation"
                    : "Student Password Reset"}
                </span>
              </div>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground pt-1">
                {authMode === "login"
                  ? "Student Sign In"
                  : authMode === "activate"
                  ? "Activate Student Account"
                  : "Reset Account Password"}
              </h1>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                {authMode === "login"
                  ? "Access your academic records, attendance thresholds, exam marks, and helpdesk."
                  : authMode === "activate"
                  ? "Verify your institutional identity with an OTP sent to your verified college email."
                  : "Request an identity verification code to set a new password."}
              </p>
            </div>

            {/* Mode Switcher Tabs */}
            <div className="grid grid-cols-2 p-1 bg-slate-100 rounded-lg text-xs font-medium">
              <button
                type="button"
                onClick={() => {
                  setAuthMode("login");
                  resetMessages();
                }}
                className={`py-1.5 rounded-md transition-all cursor-pointer ${
                  authMode === "login"
                    ? "bg-white text-blue-700 font-bold shadow-xs"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => {
                  setAuthMode("activate");
                  setOtpSent(false);
                  setOtpCode("");
                  resetMessages();
                }}
                className={`py-1.5 rounded-md transition-all cursor-pointer ${
                  authMode === "activate"
                    ? "bg-white text-blue-700 font-bold shadow-xs"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Activate Account
              </button>
            </div>

            {/* Feedback Notifications */}
            {error && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700 text-center font-medium leading-relaxed">
                {error}
              </div>
            )}
            {successMsg && (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-700 text-center font-medium leading-relaxed">
                {successMsg}
              </div>
            )}

            {/* TAB 1: EXISTING STUDENT SIGN IN */}
            {authMode === "login" && (
              <form onSubmit={handleLoginSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-foreground flex items-center justify-between">
                    <span>Registration Number</span>
                    <span className="text-[10px] text-muted-foreground font-normal">e.g. 251FA04001</span>
                  </label>
                  <div className="relative">
                    <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                      type="text"
                      required
                      placeholder="Enter your VFSTR registration number"
                      value={studentId}
                      onChange={(e) => setStudentId(e.target.value.toUpperCase())}
                      className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-medium tracking-wide uppercase focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-foreground">Password</label>
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode("reset");
                        setOtpSent(false);
                        setRegdNo(studentId);
                        resetMessages();
                      }}
                      className="text-[11px] font-medium text-blue-600 hover:text-blue-700 cursor-pointer"
                    >
                      Forgot password?
                    </button>
                  </div>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                      type="password"
                      required
                      placeholder="Enter your account password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-medium focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 text-xs sm:text-sm font-semibold text-white shadow-md shadow-blue-600/20 hover:bg-blue-700 disabled:opacity-50 transition-all cursor-pointer"
                >
                  {isLoading ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <>
                      <span>Sign In</span>
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>

                <div className="pt-2 text-center text-xs text-muted-foreground">
                  <span>First time logging in? </span>
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode("activate");
                      setRegdNo(studentId);
                      setOtpSent(false);
                      resetMessages();
                    }}
                    className="font-semibold text-blue-600 hover:underline cursor-pointer"
                  >
                    Activate your account
                  </button>
                </div>
              </form>
            )}

            {/* TAB 2: FIRST-TIME ACCOUNT ACTIVATION */}
            {authMode === "activate" && (
              <div className="space-y-4">
                {!otpSent ? (
                  /* Step 1: Enter Registration Number to Dispatch OTP */
                  <form onSubmit={handleRequestActivationOtp} className="space-y-4">
                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-foreground flex items-center justify-between">
                        <span>Registration Number</span>
                        <span className="text-[10px] text-muted-foreground font-normal">VFSTR Series 251FA...</span>
                      </label>
                      <div className="relative">
                        <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                          type="text"
                          required
                          placeholder="e.g. 251FA04001"
                          value={regdNo}
                          onChange={(e) => setRegdNo(e.target.value.toUpperCase())}
                          className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-medium tracking-wide uppercase focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                      </div>
                    </div>

                    <div className="rounded-xl border border-blue-100 bg-blue-50/70 p-3 text-xs text-blue-800 space-y-1">
                      <p className="font-semibold">Identity Verification Notice:</p>
                      <p className="text-[11px] text-blue-700 leading-relaxed">
                        A 6-digit verification code will be dispatched to your verified institutional email (@vignan.ac.in).
                      </p>
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading}
                      className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 text-xs sm:text-sm font-semibold text-white shadow-md shadow-blue-600/20 hover:bg-blue-700 disabled:opacity-50 transition-all cursor-pointer"
                    >
                      {isLoading ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <Mail className="h-4 w-4" />
                          <span>Dispatch Verification Code</span>
                        </>
                      )}
                    </button>
                  </form>
                ) : (
                  /* Step 2: Enter OTP Code and Create Secure Password */
                  <form onSubmit={handleVerifyAndActivate} className="space-y-3.5">
                    <div className="rounded-xl border border-slate-200 bg-slate-50 p-2.5 text-xs flex items-center justify-between">
                      <div>
                        <span className="text-muted-foreground">Registration: </span>
                        <span className="font-bold text-foreground">{regdNo}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setOtpSent(false)}
                        className="text-[11px] text-blue-600 hover:underline"
                      >
                        Change
                      </button>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-foreground flex items-center justify-between">
                        <span>6-Digit Verification Code</span>
                        <span className="text-[10px] text-emerald-600 font-medium">Valid for 10 mins</span>
                      </label>
                      <div className="relative">
                        <KeyRound className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                          type="text"
                          required
                          maxLength={6}
                          placeholder="Enter 6-digit OTP"
                          value={otpCode}
                          onChange={(e) => setOtpCode(e.target.value.replace(/[^0-9]/g, ""))}
                          className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-mono tracking-widest text-center focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-foreground">Create New Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                          type="password"
                          required
                          placeholder="Min 8 chars with letter & number"
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-medium focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-foreground">Confirm Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                          type="password"
                          required
                          placeholder="Re-enter password"
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-medium focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading}
                      className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 text-xs sm:text-sm font-semibold text-white shadow-md shadow-blue-600/20 hover:bg-blue-700 disabled:opacity-50 transition-all cursor-pointer"
                    >
                      {isLoading ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <CheckCircle2 className="h-4 w-4" />
                          <span>Verify & Activate Account</span>
                        </>
                      )}
                    </button>
                  </form>
                )}
              </div>
            )}

            {/* TAB 3: PASSWORD RESET */}
            {authMode === "reset" && (
              <div className="space-y-4">
                {!otpSent ? (
                  <form onSubmit={handleRequestResetOtp} className="space-y-4">
                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-foreground flex items-center justify-between">
                        <span>Registration Number</span>
                        <span className="text-[10px] text-muted-foreground font-normal">VFSTR Series 251FA...</span>
                      </label>
                      <div className="relative">
                        <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                          type="text"
                          required
                          placeholder="e.g. 251FA04001"
                          value={regdNo}
                          onChange={(e) => setRegdNo(e.target.value.toUpperCase())}
                          className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-medium tracking-wide uppercase focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading}
                      className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 text-xs sm:text-sm font-semibold text-white shadow-md shadow-blue-600/20 hover:bg-blue-700 disabled:opacity-50 transition-all cursor-pointer"
                    >
                      {isLoading ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <Mail className="h-4 w-4" />
                          <span>Send Password Reset Code</span>
                        </>
                      )}
                    </button>

                    <div className="text-center text-xs text-muted-foreground pt-1">
                      <button
                        type="button"
                        onClick={() => {
                          setAuthMode("login");
                          resetMessages();
                        }}
                        className="text-blue-600 hover:underline cursor-pointer"
                      >
                        Return to Sign In
                      </button>
                    </div>
                  </form>
                ) : (
                  <form onSubmit={handleVerifyAndReset} className="space-y-3.5">
                    <div className="rounded-xl border border-slate-200 bg-slate-50 p-2.5 text-xs flex items-center justify-between">
                      <div>
                        <span className="text-muted-foreground">Registration: </span>
                        <span className="font-bold text-foreground">{regdNo}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setOtpSent(false)}
                        className="text-[11px] text-blue-600 hover:underline"
                      >
                        Change
                      </button>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-foreground flex items-center justify-between">
                        <span>6-Digit Verification Code</span>
                        <span className="text-[10px] text-emerald-600 font-medium">Valid for 10 mins</span>
                      </label>
                      <div className="relative">
                        <KeyRound className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                          type="text"
                          required
                          maxLength={6}
                          placeholder="Enter 6-digit OTP"
                          value={otpCode}
                          onChange={(e) => setOtpCode(e.target.value.replace(/[^0-9]/g, ""))}
                          className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-mono tracking-widest text-center focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-foreground">New Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                          type="password"
                          required
                          placeholder="Min 8 chars with letter & number"
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-medium focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-foreground">Confirm New Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                          type="password"
                          required
                          placeholder="Re-enter new password"
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          className="w-full rounded-xl border border-slate-200 bg-card pl-10 pr-4 py-2.5 text-xs sm:text-sm font-medium focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading}
                      className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 text-xs sm:text-sm font-semibold text-white shadow-md shadow-blue-600/20 hover:bg-blue-700 disabled:opacity-50 transition-all cursor-pointer"
                    >
                      {isLoading ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <CheckCircle2 className="h-4 w-4" />
                          <span>Reset Password & Sign In</span>
                        </>
                      )}
                    </button>
                  </form>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full border-t border-slate-200/80 bg-card/60 py-4 text-center text-xs text-muted-foreground">
        <p>© {new Date().getFullYear()} Vignan Foundation for Science, Technology and Research (VFSTR). Protected by University Authentication.</p>
      </footer>
    </div>
  );
};
