"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Bot,
  Send,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  Lock,
  Info,
  X,
  Layers,
  Compass,
  ThumbsUp,
  ThumbsDown,
  Check,
  Cpu,
  Zap,
} from "lucide-react";
import { MarkdownText } from "@/components/ui/markdown-text";
import { processQuery, ConversationTurn } from "@/lib/ai-engine";
import { getStudentData, StudentFullData } from "@/data/students-db";
import { useLanguage } from "@/context/LanguageContext";
import { apiClient } from "@/lib/api-client";

interface InteractiveLivePreviewProps {
  onExploreMore?: () => void;
}

export const InteractiveLivePreview: React.FC<InteractiveLivePreviewProps> = ({
  onExploreMore,
}) => {
  const { t } = useLanguage();

  const [studentData] = useState<StudentFullData>(() =>
    getStudentData("251FA04E13")
  );
  const [messages, setMessages] = useState<ConversationTurn[]>([]);
  const [inputQuery, setInputQuery] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [activeCapability, setActiveCapability] = useState<
    "offline" | "rls" | "agents" | null
  >(null);
  const [showRlsDetails, setShowRlsDetails] = useState(false);

  // 3D Tilt and Parallax State (Default is 3D)
  const [tilt, setTilt] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [glare, setGlare] = useState<{ x: number; y: number; opacity: number }>({
    x: 50,
    y: 50,
    opacity: 0,
  });
  const [isHovering, setIsHovering] = useState(false);
  const [is3DEnabled, setIs3DEnabled] = useState(true);

  const [feedbackState, setFeedbackState] = useState<Record<number, "up" | "down">>({});
  const [feedbackSubmitting, setFeedbackSubmitting] = useState<Record<number, boolean>>({});

  const cardRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Robust scroll helper for landing page section redirects with navbar clearance
  const scrollToSection = (sectionId: string) => {
    const rawId = sectionId.replace(/^#/, "");
    const candidateIds = [
      rawId,
      rawId === "trust-security" ? "trust-&-security" : "trust-security",
      "trust-&-security",
      "trust-security",
      "features",
      "how-it-works",
    ];

    let targetEl: HTMLElement | null = null;
    for (const id of candidateIds) {
      const found = document.getElementById(id);
      if (found) {
        targetEl = found;
        break;
      }
    }

    if (targetEl) {
      const navOffset = 76;
      const elementPosition = targetEl.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - navOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });

      try {
        window.history.pushState(null, "", `#${rawId}`);
      } catch {
        window.location.hash = `#${rawId}`;
      }
    } else {
      window.location.hash = `#${rawId}`;
    }
  };

  const handlePreviewFeedback = async (
    index: number,
    rating: "up" | "down",
    msg: ConversationTurn
  ) => {
    if (feedbackSubmitting[index]) return;
    setFeedbackSubmitting((prev) => ({ ...prev, [index]: true }));
    setFeedbackState((prev) => ({ ...prev, [index]: rating }));

    const contextMsgs = messages.slice(0, index + 1).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      await apiClient.sendFeedback(
        msg.conversationId || "preview-session",
        msg.messageId || `preview-msg-${index}`,
        rating,
        undefined,
        contextMsgs,
        msg.content
      );
    } catch (e) {
      console.warn("Feedback submission error:", e);
    } finally {
      setFeedbackSubmitting((prev) => ({ ...prev, [index]: false }));
    }
  };

  // Initialize conversation with "What can you do?"
  useEffect(() => {
    const initialQ = "What can you do?";
    const initialResp = processQuery(initialQ, [], undefined, studentData);

    setMessages([
      {
        role: "user",
        content: initialQ,
      },
      {
        role: "assistant",
        content: initialResp.text,
        responseMeta: initialResp,
      },
    ]);
  }, [studentData]);

  // Auto-scroll chat
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isTyping]);

  // Mouse Move 3D Calculation
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!is3DEnabled || !cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * -12;
    const rotateY = ((x - centerX) / centerX) * 12;

    setTilt({ x: rotateX, y: rotateY });
    setGlare({
      x: (x / rect.width) * 100,
      y: (y / rect.height) * 100,
      opacity: 1,
    });
    setIsHovering(true);
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
    setTilt({ x: 0, y: 0 });
    setGlare((prev) => ({ ...prev, opacity: 0 }));
  };

  const handleSend = (textToSend?: string) => {
    const query = (textToSend || inputQuery).trim();
    if (!query || isTyping) return;

    const lower = query.toLowerCase();
    if (
      lower.includes("offline") ||
      lower.includes("8b") ||
      lower.includes("local") ||
      lower.includes("neural")
    ) {
      setActiveCapability("offline");
    } else if (
      lower.includes("security") ||
      lower.includes("rls") ||
      lower.includes("leakage") ||
      lower.includes("guardrail")
    ) {
      setActiveCapability("rls");
    } else if (
      lower.includes("agent") ||
      lower.includes("federated") ||
      lower.includes("specialized") ||
      lower.includes("campus")
    ) {
      setActiveCapability("agents");
    }

    const updatedHistory: ConversationTurn[] = [
      ...messages,
      { role: "user", content: query },
    ];
    setMessages(updatedHistory);
    setInputQuery("");
    setIsTyping(true);

    setTimeout(() => {
      const response = processQuery(
        query,
        updatedHistory,
        undefined,
        studentData
      );

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.text,
          responseMeta: response,
        },
      ]);
      setIsTyping(false);
    }, 400);
  };

  const handleResetChat = () => {
    const initialQ = "What can you do?";
    const initialResp = processQuery(initialQ, [], undefined, studentData);
    setMessages([
      { role: "user", content: initialQ },
      { role: "assistant", content: initialResp.text, responseMeta: initialResp },
    ]);
    setActiveCapability(null);
  };

  // Dynamic 3D Transform and Shadow calculations
  const transformStyle = is3DEnabled
    ? isHovering
      ? `perspective(1200px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale3d(1.02, 1.02, 1.02)`
      : undefined
    : "none";

  const dynamicShadow = is3DEnabled && isHovering
    ? `${-tilt.y * 1.5}px ${tilt.x * 1.5 + 24}px 40px -10px rgba(37, 99, 235, 0.22), 0 10px 25px -5px rgba(0, 0, 0, 0.08)`
    : undefined;

  return (
    <div
      className="relative select-none"
      style={{ perspective: is3DEnabled ? "1200px" : "none" }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <style>{`
        @keyframes idleFloat3D {
          0%, 100% {
            transform: perspective(1200px) rotateX(3.5deg) rotateY(-4deg) translateY(0px);
          }
          50% {
            transform: perspective(1200px) rotateX(-3.5deg) rotateY(4deg) translateY(-10px);
          }
        }
        @keyframes orbitalBadge1 {
          0%, 100% {
            transform: translateZ(55px) translateY(0px) rotate(0deg);
          }
          50% {
            transform: translateZ(65px) translateY(-6px) rotate(1.5deg);
          }
        }
        @keyframes orbitalBadge2 {
          0%, 100% {
            transform: translateZ(50px) translateY(0px) rotate(0deg);
          }
          50% {
            transform: translateZ(60px) translateY(6px) rotate(-1.5deg);
          }
        }
      `}</style>

      {/* Floating 3D Ambient Glowing Backdrops (visible in 3D mode) */}
      {is3DEnabled && (
        <div
          className="pointer-events-none absolute -inset-3 rounded-3xl bg-gradient-to-tr from-blue-600/20 via-indigo-500/15 to-emerald-400/20 blur-2xl transition-all duration-700"
          style={{
            transform: isHovering
              ? `translateZ(-40px) rotateX(${tilt.x * 0.5}deg) rotateY(${tilt.y * 0.5}deg)`
              : "translateZ(-40px)",
          }}
        />
      )}

      {/* Floating 3D Hologram Badge 1 (Top Right Satellite) */}
      {is3DEnabled && (
        <div
          className="pointer-events-none absolute -top-4 -right-3 z-30 hidden sm:flex items-center gap-1.5 rounded-full border border-blue-200/80 bg-white/95 px-3 py-1 text-[11px] font-semibold text-blue-700 shadow-xl backdrop-blur-md"
          style={{
            transform: isHovering
              ? `translateZ(55px) translateX(${tilt.y * 1.2}px) translateY(${-tilt.x * 1.2}px)`
              : undefined,
            animation: !isHovering ? "orbitalBadge1 5s ease-in-out infinite" : undefined,
            transformStyle: "preserve-3d",
          }}
        >
          <Sparkles className="h-3 w-3 text-blue-600 animate-spin" style={{ animationDuration: "6s" }} />
          <span>3D Grounded Telemetry</span>
        </div>
      )}

      {/* Floating 3D Hologram Badge 2 (Top Left Satellite) */}
      {is3DEnabled && (
        <div
          className="pointer-events-none absolute -top-4 -left-3 z-30 hidden sm:flex items-center gap-1.5 rounded-full border border-emerald-200/80 bg-white/95 px-3 py-1 text-[11px] font-semibold text-emerald-700 shadow-xl backdrop-blur-md"
          style={{
            transform: isHovering
              ? `translateZ(50px) translateX(${tilt.y * 1.1}px) translateY(${-tilt.x * 1.1}px)`
              : undefined,
            animation: !isHovering ? "orbitalBadge2 5.5s ease-in-out infinite" : undefined,
            transformStyle: "preserve-3d",
          }}
        >
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
          </span>
          <span>Sub-100ms Inference</span>
        </div>
      )}

      {/* Main Card Surface with 3D or flat 2D */}
      <div
        ref={cardRef}
        id="hero-live-preview-card"
        className={`relative flex flex-col rounded-2xl border border-slate-200/90 bg-card/95 shadow-2xl backdrop-blur-md transition-transform ${
          is3DEnabled && !isHovering ? "animate-[idleFloat3D_6s_ease-in-out_infinite]" : ""
        }`}
        style={{
          transform: transformStyle,
          boxShadow: dynamicShadow,
          transformStyle: is3DEnabled ? "preserve-3d" : "flat",
          transition: isHovering ? "transform 0.12s cubic-bezier(0.2, 0, 0.2, 1)" : "transform 0.8s ease-out, box-shadow 0.8s ease-out",
        }}
      >
        {/* Specular Dynamic Glare Sheen (Active only in 3D mode) */}
        {is3DEnabled && (
          <div
            className="pointer-events-none absolute inset-0 rounded-2xl transition-opacity duration-300 z-0 overflow-hidden"
            style={{
              opacity: glare.opacity ? 0.35 : 0,
              background: `radial-gradient(circle 350px at ${glare.x}% ${glare.y}%, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.1) 40%, transparent 80%)`,
              transform: "translateZ(5px)",
            }}
          />
        )}

        {/* Card Header Layer */}
        <div
          className="flex items-center justify-between border-b border-slate-100 px-5 py-3.5 transition-transform duration-200"
          style={{ transform: is3DEnabled ? "translateZ(32px)" : "none", transformStyle: is3DEnabled ? "preserve-3d" : "flat" }}
        >
          <div className="flex items-center gap-3">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-blue-700 text-white shadow-lg shadow-blue-600/30">
              <Bot className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-500 border-2 border-white" />
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-foreground">
                  {t.studentHelpdesk || "VIGNAN-AI"}
                </span>
                <span className="rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-semibold text-blue-700 border border-blue-200">
                  VIGNAN-AI · {is3DEnabled ? "3D" : "2D"}
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Compass className="h-3 w-3 text-blue-500 animate-spin" style={{ animationDuration: "12s" }} />
                <span>{is3DEnabled ? "Spatial 3D Preview" : "Flat 2D Standard View"}</span>
              </div>
            </div>
          </div>

          {/* Clean Header Controls: Separated 3D/2D Toggle & Reset */}
          <div className="flex items-center gap-2">
            {/* Dedicated 3D / 2D Spatial Mode Toggle Button */}
            <button
              type="button"
              onClick={() => setIs3DEnabled((prev) => !prev)}
              className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold shadow-xs transition-all cursor-pointer ${
                is3DEnabled
                  ? "border-blue-500 bg-blue-50 text-blue-700 ring-2 ring-blue-500/20 shadow-blue-500/10 font-bold"
                  : "border-slate-300 bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
              title={
                is3DEnabled
                  ? "3D Spatial Mode Active • Click to switch to 2D Flat Mode"
                  : "2D Flat Mode Active • Click to switch to 3D Spatial Mode"
              }
              aria-label="Toggle 3D or 2D mode"
            >
              <Layers className={`h-3.5 w-3.5 ${is3DEnabled ? "text-blue-600" : "text-slate-500"}`} />
              <span>{is3DEnabled ? "3D Mode" : "2D Mode"}</span>
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  is3DEnabled ? "bg-blue-600 animate-pulse" : "bg-slate-400"
                }`}
              />
            </button>

            {/* Reset Chat Button */}
            <button
              type="button"
              onClick={handleResetChat}
              className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 text-muted-foreground hover:text-foreground hover:bg-muted transition-colors cursor-pointer"
              title="Reset conversation to initial prompt"
              aria-label="Reset conversation"
            >
              <RotateCcw className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        {/* Scrollable Conversation Stream */}
        <div
          ref={chatContainerRef}
          className="max-h-[310px] min-h-[250px] overflow-y-auto px-5 py-4 space-y-3.5 text-sm"
          style={{ transform: is3DEnabled ? "translateZ(24px)" : "none", transformStyle: is3DEnabled ? "preserve-3d" : "flat" }}
        >
          {messages.map((msg, idx) => {
            const isUser = msg.role === "user";
            const meta = msg.responseMeta;

            return (
              <div
                key={idx}
                className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
                style={{
                  transform: is3DEnabled ? (isUser ? "translateZ(36px)" : "translateZ(28px)") : "none",
                  transformStyle: is3DEnabled ? "preserve-3d" : "flat",
                }}
              >
                {/* User Message Bubble */}
                {isUser ? (
                  <div className="w-fit max-w-[85%] rounded-2xl rounded-tr-sm bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2.5 text-white shadow-lg shadow-blue-600/20 font-medium">
                    {msg.content}
                  </div>
                ) : (
                  /* Assistant Message Bubble */
                  <div className="w-fit max-w-[94%] space-y-2.5 rounded-2xl rounded-tl-sm border border-slate-200/80 bg-slate-50/95 dark:bg-slate-800/80 px-4 py-3 text-foreground shadow-md">
                    {/* Header meta */}
                    <div className="flex items-center gap-2 border-b border-slate-200/60 pb-1.5 text-[11px] text-muted-foreground">
                      <span className="font-semibold text-blue-700">
                        {meta?.sourceAgent || "VIGNAN-AI Core"}
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1 text-emerald-700 font-medium">
                        <Lock className="h-3 w-3" />
                        RLS Authorized
                      </span>
                    </div>

                    {/* Main text content rendered with full Markdown formatting */}
                    <div className="text-xs sm:text-sm leading-relaxed text-slate-800 dark:text-slate-100 font-normal">
                      <MarkdownText text={msg.content} />
                    </div>

                    {/* Quick Section Redirect Buttons (Features, How It Works, Trust & Security) */}
                    <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex flex-wrap items-center gap-2 relative z-30 pointer-events-auto">
                      <a
                        href="#features"
                        onClick={(e) => {
                          e.preventDefault();
                          scrollToSection("features");
                        }}
                        className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 text-xs font-semibold shadow-xs hover:shadow transition-all active:scale-95 cursor-pointer no-underline"
                        title="Explore VIGNAN-AI Features"
                      >
                        <Sparkles className="h-3.5 w-3.5" />
                        <span>Features</span>
                      </a>
                      <a
                        href="#how-it-works"
                        onClick={(e) => {
                          e.preventDefault();
                          scrollToSection("how-it-works");
                        }}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 hover:text-blue-600 text-slate-700 px-3 py-1.5 text-xs font-semibold shadow-xs transition-all active:scale-95 cursor-pointer no-underline dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200"
                        title="See How VIGNAN-AI Works"
                      >
                        <Compass className="h-3.5 w-3.5 text-blue-500" />
                        <span>How It Works</span>
                      </a>
                      <a
                        href="#trust-&-security"
                        onClick={(e) => {
                          e.preventDefault();
                          scrollToSection("trust-&-security");
                        }}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-300 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 px-3 py-1.5 text-xs font-semibold shadow-xs transition-all active:scale-95 cursor-pointer no-underline"
                        title="Inspect Trust & Row-Level Security"
                      >
                        <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
                        <span>Trust & Security</span>
                      </a>
                    </div>

                    {/* Thumbs Feedback Controls */}
                    <div className="mt-2 pt-1.5 border-t border-slate-200/60 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1">
                        <span className="text-[10px] text-muted-foreground font-medium">Helpful?</span>
                        <button
                          type="button"
                          onClick={() => handlePreviewFeedback(idx, "up", msg)}
                          disabled={feedbackSubmitting[idx]}
                          className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[11px] font-medium transition-all cursor-pointer ${
                            feedbackState[idx] === "up"
                              ? "bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold"
                              : "hover:bg-slate-200/70 text-slate-500 border border-slate-200"
                          }`}
                          title="Thumbs up: Helpful response"
                        >
                          <ThumbsUp className={`h-2.5 w-2.5 ${feedbackState[idx] === "up" ? "fill-emerald-600 text-emerald-600" : ""}`} />
                          <span>👍</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => handlePreviewFeedback(idx, "down", msg)}
                          disabled={feedbackSubmitting[idx]}
                          className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[11px] font-medium transition-all cursor-pointer ${
                            feedbackState[idx] === "down"
                              ? "bg-rose-100 text-rose-800 border border-rose-300 font-bold"
                              : "hover:bg-slate-200/70 text-slate-500 border border-slate-200"
                          }`}
                          title="Thumbs down: Mark response as not helpful"
                        >
                          <ThumbsDown className={`h-2.5 w-2.5 ${feedbackState[idx] === "down" ? "fill-rose-600 text-rose-600" : ""}`} />
                          <span>👎</span>
                        </button>
                      </div>

                      {feedbackState[idx] === "up" && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full animate-in fade-in duration-200">
                          <Check className="h-2.5 w-2.5 text-emerald-600" />
                          Feedback recorded
                        </span>
                      )}
                      {feedbackState[idx] === "down" && (
                        <span className="text-[10px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                          Feedback recorded
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          {/* Typing Animation */}
          {isTyping && (
            <div className="flex items-start" style={{ transform: is3DEnabled ? "translateZ(25px)" : "none" }}>
              <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm border border-slate-200/80 bg-slate-50 px-4 py-2.5 text-xs text-muted-foreground shadow-sm">
                <span className="font-semibold text-blue-600">VIGNAN-AI</span>
                <span>is querying institutional records...</span>
                <span className="flex gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-bounce" />
                  <span
                    className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-bounce"
                    style={{ animationDelay: "150ms" }}
                  />
                  <span
                    className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  />
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Interactive Query Input Box */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="border-t border-slate-100 px-4 py-3 bg-white"
          style={{ transform: is3DEnabled ? "translateZ(36px)" : "none", transformStyle: is3DEnabled ? "preserve-3d" : "flat" }}
        >
          <div className="relative flex items-center">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask VIGNAN-AI anything (attendance, exams, fees, policies)..."
              disabled={isTyping}
              className="w-full rounded-xl border border-slate-200 bg-muted/30 py-2 pl-3 pr-16 text-xs text-foreground placeholder:text-muted-foreground focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50"
            />
            {inputQuery && (
              <button
                type="button"
                onClick={() => setInputQuery("")}
                className="absolute right-9 text-slate-400 hover:text-slate-600 p-1"
                aria-label="Clear input"
              >
                <X className="h-3 w-3" />
              </button>
            )}
            <button
              type="submit"
              disabled={!inputQuery.trim() || isTyping}
              className="absolute right-1.5 flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-white shadow-md shadow-blue-600/30 hover:bg-blue-700 transition-all disabled:opacity-30 disabled:cursor-not-allowed active:scale-95 cursor-pointer"
              aria-label="Send message"
            >
              <Send className="h-3.5 w-3.5" />
            </button>
          </div>
        </form>

        {/* Meaningful Architecture & Capabilities Row */}
        <div
          className="grid grid-cols-3 gap-2 border-t border-slate-100 bg-slate-50/80 p-3 text-center"
          style={{ transform: is3DEnabled ? "translateZ(40px)" : "none", transformStyle: is3DEnabled ? "preserve-3d" : "flat" }}
        >
          {/* 1. Hybrid 3-Tier AI */}
          <button
            type="button"
            onClick={() => handleSend("Tell me about the 3-tier hybrid AI architecture")}
            className={`group rounded-xl p-2.5 transition-all text-left flex flex-col justify-between shadow-xs cursor-pointer ${
              activeCapability === "offline"
                ? "bg-blue-100/90 border-2 border-blue-500 ring-2 ring-blue-400/20 scale-[1.02]"
                : "bg-blue-50/80 hover:bg-blue-100/70 border border-blue-100 hover:scale-[1.02]"
            }`}
            title="Click to learn about the 3-tier hybrid AI architecture"
          >
            <div className="flex items-center justify-between">
              <span className="text-lg font-black text-blue-900">3-Tier</span>
              <Cpu className="h-3.5 w-3.5 text-blue-600 group-hover:scale-110 transition-transform" />
            </div>
            <div className="mt-1">
              <div className="text-[11px] font-bold text-blue-800 leading-tight">Hybrid 3-Tier AI</div>
              <div className="text-[9px] text-blue-600/80 font-medium truncate">Local ML + Grounded LLM</div>
            </div>
          </button>

          {/* 2. Row-Level Security & PII Redaction */}
          <button
            type="button"
            onClick={() => handleSend("How does Row-Level Security protect my data?")}
            className={`group rounded-xl p-2.5 transition-all text-left flex flex-col justify-between shadow-xs cursor-pointer ${
              activeCapability === "rls"
                ? "bg-emerald-100/90 border-2 border-emerald-500 ring-2 ring-emerald-400/20 scale-[1.02]"
                : "bg-emerald-50/80 hover:bg-emerald-100/70 border border-emerald-100 hover:scale-[1.02]"
            }`}
            title="Click to learn about deterministic Row-Level Security and PII redaction"
          >
            <div className="flex items-center justify-between">
              <span className="text-lg font-black text-emerald-900">0%</span>
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600 group-hover:scale-110 transition-transform" />
            </div>
            <div className="mt-1">
              <div className="text-[11px] font-bold text-emerald-800 leading-tight">Data Leakage</div>
              <div className="text-[9px] text-emerald-600/80 font-medium truncate">PII-Redacted & RLAC Guarded</div>
            </div>
          </button>

          {/* 3. Campus Intents & Domain Modules */}
          <button
            type="button"
            onClick={() => handleSend("What are the 18 campus intents & domain modules?")}
            className={`group rounded-xl p-2.5 transition-all text-left flex flex-col justify-between shadow-xs cursor-pointer ${
              activeCapability === "agents"
                ? "bg-indigo-100/90 border-2 border-indigo-500 ring-2 ring-indigo-400/20 scale-[1.02]"
                : "bg-indigo-50/80 hover:bg-indigo-100/70 border border-indigo-100 hover:scale-[1.02]"
            }`}
            title="Click to view the 18 campus intents & specialized domain modules"
          >
            <div className="flex items-center justify-between">
              <span className="text-lg font-black text-indigo-900">18</span>
              <Zap className="h-3.5 w-3.5 text-indigo-600 group-hover:scale-110 transition-transform" />
            </div>
            <div className="mt-1">
              <div className="text-[11px] font-bold text-indigo-800 leading-tight">Campus Intents</div>
              <div className="text-[9px] text-indigo-600/80 font-medium truncate">18 ML & Domain Modules</div>
            </div>
          </button>
        </div>
      </div>

      {/* Floating Interactive RLS Guardrail Badge */}
      <div
        className="relative"
        style={{
          transform: is3DEnabled && isHovering
            ? `translateZ(65px) translateX(${tilt.y * 0.8}px) translateY(${-tilt.x * 0.8}px)`
            : is3DEnabled ? "translateZ(65px)" : "none",
          transformStyle: is3DEnabled ? "preserve-3d" : "flat",
          transition: "transform 0.15s ease-out",
        }}
      >
        <button
          type="button"
          onClick={() => setShowRlsDetails((prev) => !prev)}
          className="absolute -bottom-5 -left-4 sm:-left-6 flex items-center gap-2 rounded-xl border border-emerald-200 bg-white/95 px-3.5 py-2.5 shadow-xl shadow-emerald-950/10 hover:border-emerald-300 hover:shadow-2xl transition-all cursor-pointer z-30 group"
          title="Click to inspect Row-Level Security verification"
        >
          <span className="relative flex h-2.5 w-2.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
          </span>
          <span className="text-xs font-semibold text-emerald-900 flex items-center gap-1">
            {t.landingRlsVerified || "RLS guardrail verified"}
            <Info className="h-3 w-3 text-emerald-600 group-hover:text-emerald-800" />
          </span>
        </button>

        {/* Expandable RLS Security Popover */}
        {showRlsDetails && (
          <div className="absolute -bottom-36 left-0 z-50 w-72 rounded-xl border border-emerald-200 bg-white p-3.5 shadow-2xl animate-in fade-in zoom-in-95 duration-200 text-xs">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <div className="flex items-center gap-1.5 font-bold text-emerald-900">
                <ShieldCheck className="h-4 w-4 text-emerald-600" />
                <span>Deterministic Row-Level Security</span>
              </div>
              <button
                type="button"
                onClick={() => setShowRlsDetails(false)}
                className="text-slate-400 hover:text-slate-600 p-0.5 cursor-pointer"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
            <div className="mt-2 space-y-1.5 text-slate-600 text-[11px] leading-relaxed">
              <p>
                <strong className="text-slate-900">Active Scope:</strong>{" "}
                <span className="font-mono text-emerald-700 bg-emerald-50 px-1 py-0.5 rounded">
                  {studentData.profile.name} ({studentData.profile.id})
                </span>
              </p>
              <p>
                VIGNAN-AI enforces mathematical data isolation. Responses only
                contain records verified against your authenticated student token.
              </p>
            </div>
            <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-muted-foreground">
              <span>Token: VFSTR-SEC-2026</span>
              <span className="text-emerald-600 font-semibold">PII-Redacted & RLAC Guarded</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
