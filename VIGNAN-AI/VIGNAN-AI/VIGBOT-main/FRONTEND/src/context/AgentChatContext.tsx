"use client";

import React, { createContext, useContext, useState, useRef, useEffect } from "react";
import {
  processQuery,
  ConversationTurn,
  QueryCategory,
  StructuredCardData,
} from "@/lib/ai-engine";
import { CURRENT_STUDENT } from "@/data/student";
import { apiClient } from "@/lib/api-client";
import { useStudent } from "@/context/StudentContext";
import { useLanguage } from "@/context/LanguageContext";
import { askAiKnowledgeBase } from "@/actions/ai-search";

// Define a minimal interface for SpeechRecognition since it's a web API that might not be in standard DOM lib yet
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
}
interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}
interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  lang: string;
  abort: () => void;
  start: () => void;
  onstart: ((this: SpeechRecognition, ev: Event) => void) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => void) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => void) | null;
  onend: ((this: SpeechRecognition, ev: Event) => void) | null;
}
interface WindowWithSpeech extends Window {
  SpeechRecognition?: { new(): SpeechRecognition };
  webkitSpeechRecognition?: { new(): SpeechRecognition };
}

interface AgentChatContextType {
  messages: ConversationTurn[];
  inputQuery: string;
  setInputQuery: (query: string) => void;
  isTyping: boolean;
  isListening: boolean;
  isMaximized: boolean;
  setIsMaximized: (val: boolean) => void;
  activeContextSubject: string | undefined;
  handleSend: (textToSend?: string, model?: "3B" | "8B") => void;
  handleResetChat: () => void;
  handleSpeechToggle: () => void;
  registerDistressCallback: (cb: () => void) => void;
}

const AgentChatContext = createContext<AgentChatContextType | undefined>(undefined);

export const AgentChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { studentData } = useStudent();
  const student = studentData?.profile || CURRENT_STUDENT;

  const { language } = useLanguage();

  const buildInitialGreeting = React.useCallback((s: typeof student, lang: string = "en"): ConversationTurn => {
    let content = `Hello ${s.name}! I am **VIGBOT**, your AI university assistant.\n\nI have securely authenticated your identity (**${s.id}**) and connected to your academic records. You can ask me anything about your **attendance**, **examination dates**, **marks**, **fees**, **curriculum progress**, or **university policies**.\n\nHow can I support your university journey today?`;
    let followUps = [
      "What is my attendance in Digital Logic design?",
      "When is my next exam?",
      "What is my fee status?",
      "How many credits do I still need to graduate?",
    ];

    if (lang === "te") {
      content = `నమస్కారం ${s.name}! నేను మీ **VIGBOT** (విశ్వవిద్యాలయ AI సహాయకుడు).\n\nమీ గుర్తింపును (**${s.id}**) విజయవంతంగా ధృవీకరించాను. మీ **హాజరు**, **పరీక్షల షెడ్యూల్**, **మార్కులు**, **ఫీజులు**, లేదా **విశ్వవిద్యాలయ విధానాల** గురించి నన్ను ఏదైనా అడగవచ్చు.\n\nఈ రోజు నేను మీకు ఎలా సహాయపడగలను?`;
      followUps = [
        "డిజిటల్ లాజిక్ డిజైన్‌లో నా హాజరు ఎంత?",
        "నా తదుపరి పరీక్ష ఎప్పుడు?",
        "నా ఫీజు బకాయిల వివరాలు చూపించు",
        "డిగ్రీ పూర్తి కావడానికి ఇంకా ఎన్ని క్రెడిట్లు కావాలి?",
      ];
    } else if (lang === "hi") {
      content = `नमस्ते ${s.name}! मैं आपका **VIGBOT** (विश्वविद्यालय AI सहायक) हूँ।\n\nमैंने आपकी पहचान (**${s.id}**) सुरक्षित रूप से प्रमाणित कर ली है। आप मुझसे अपनी **उपस्थिति**, **परीक्षा तिथियों**, **अंकों**, **फीस स्थिति** या **विश्वविद्यालय नीतियों** के बारे में कुछ भी पूछ सकते हैं।\n\nआज मैं आपकी क्या सहायता कर सकता हूँ?`;
      followUps = [
        "डिजिटल लॉजिक डिज़ाइन में मेरी उपस्थिति कितनी है?",
        "मेरी अगली परीक्षा कब है?",
        "मेरी फीस स्थिति क्या है?",
        "ग्रेजुएशन के लिए मुझे अभी कितने क्रेडिट चाहिए?",
      ];
    }

    return {
      role: "assistant",
      content,
      responseMeta: {
        text: "",
        category: "PERSONAL_DATA",
        sourceAgent: "VIGBOT",
        authorizedFor: s.id,
        isDistress: false,
        suggestedFollowUps: followUps,
      },
    };
  }, []);

  const [messages, setMessages] = useState<ConversationTurn[]>(() => [buildInitialGreeting(student, language)]);

  const lastStudentIdRef = useRef(student.id);
  const lastLangRef = useRef(language);
  useEffect(() => {
    if (lastLangRef.current !== language || lastStudentIdRef.current !== student.id) {
      lastLangRef.current = language;
      lastStudentIdRef.current = student.id;
      setMessages([buildInitialGreeting(student, language)]);
    }
  }, [language, student.id, student, buildInitialGreeting]);
  useEffect(() => {
    if (lastStudentIdRef.current !== student.id) {
      lastStudentIdRef.current = student.id;
      setMessages([buildInitialGreeting(student)]);
    }
  }, [student.id, student, buildInitialGreeting]);

  const [inputQuery, setInputQuery] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [activeContextSubject, setActiveContextSubject] = useState<string | undefined>("Digital Logic design");

  const distressCallbackRef = useRef<(() => void) | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const stopListening = () => {
    setIsListening(false);
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {
        // ignore
      }
      recognitionRef.current = null;
    }
    if (mediaStreamRef.current) {
      try {
        mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      } catch {
        // ignore
      }
      mediaStreamRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      stopListening();
    };
  }, []);

  const registerDistressCallback = (cb: () => void) => {
    distressCallbackRef.current = cb;
  };

  const normalizeModelName = (rawModel?: string | null, selectedModel: "3B" | "8B" = "8B") => {
    const modelName = rawModel?.trim();
    if (!modelName || modelName === "database-direct") {
      return "hybrid-3tier";
    }

    return modelName;
  };

  const handleSend = async (textToSend?: string, model: "3B" | "8B" = "8B") => {
    const query = (textToSend || inputQuery).trim();
    if (!query || isTyping) return;

    // Append user message
    const newHistory: ConversationTurn[] = [...messages, { role: "user", content: query }];
    setMessages(newHistory);
    setInputQuery("");
    setIsTyping(true);

    try {
      // 1. Try Live FastAPI Backend Call
      const backendResp = await apiClient.sendMessage(query, language, model);
      if (backendResp) {
              const categoryStr = (backendResp.category as string) || "PERSONAL_DATA";
              let mappedRedirectPath: string | undefined = undefined;
              
              const qLower = query.toLowerCase();
              if (categoryStr === "ATTENDANCE" || qLower.includes("attendance")) mappedRedirectPath = "attendance";
              else if (categoryStr === "EXAMS" || qLower.includes("exam")) mappedRedirectPath = "exams";
              else if (categoryStr === "FEES" || qLower.includes("fee")) mappedRedirectPath = "fees";
              else if (categoryStr === "TIMETABLE" || qLower.includes("timetable") || qLower.includes("schedule")) mappedRedirectPath = "timetable";
              else if (categoryStr === "MARKS" || qLower.includes("mark") || qLower.includes("score") || qLower.includes("grade") || qLower.includes("cgpa")) mappedRedirectPath = "marks";
              else if (categoryStr === "CURRICULUM" || qLower.includes("curriculum") || qLower.includes("credit")) mappedRedirectPath = "curriculum";
              else if (categoryStr === "FACULTY" || qLower.includes("faculty") || qLower.includes("teacher") || qLower.includes("mentor")) mappedRedirectPath = "faculty";
              else if (categoryStr === "POLICIES") mappedRedirectPath = "policies";
              else if (categoryStr === "CIRCULARS") mappedRedirectPath = "circulars";
              else if (categoryStr === "CALENDAR") mappedRedirectPath = "calendar";
              else if (categoryStr === "CLUBS") mappedRedirectPath = "clubs";
              else if (categoryStr === "LOST_AND_FOUND") mappedRedirectPath = "lost-and-found";
              else if (categoryStr === "BOOKINGS") mappedRedirectPath = "bookings";
              else if (categoryStr === "SERVICES") mappedRedirectPath = "services";
              else if (categoryStr === "MAP") mappedRedirectPath = "map";
              else if (categoryStr === "EVENTS") mappedRedirectPath = "events";
              else if (categoryStr === "HOSTEL") mappedRedirectPath = "hostel";
              else if (categoryStr === "MARKETPLACE") mappedRedirectPath = "marketplace";
              else if (categoryStr === "CAREER") mappedRedirectPath = "career";
              else if (categoryStr === "GAMIFICATION") mappedRedirectPath = "gamification";
              else if (categoryStr === "TRANSPORT") mappedRedirectPath = "transport";
              else if (categoryStr === "ALUMNI") mappedRedirectPath = "alumni";
              else if (categoryStr === "WELLNESS") mappedRedirectPath = "wellness";
              else if (categoryStr === "POLLING") mappedRedirectPath = "polling";

              setMessages((prev) => [
                ...prev,
                {
                  role: "assistant",
                  content: backendResp.content,
                  messageId: backendResp.message_id,
                  conversationId: backendResp.conversation_id,
                  responseMeta: {
                    text: backendResp.content,
                    category: categoryStr as QueryCategory,
                    sourceAgent: backendResp.source_agent || "VIGBOT (Live FastAPI Backend)",
                    authorizedFor: student.id,
                    isDistress: backendResp.is_distress,
                    structuredCard: backendResp.structured_card as StructuredCardData,
                    suggestedFollowUps: backendResp.suggested_follow_ups,
                    llm_provider: backendResp.llm_provider || "local",
                    model_used: normalizeModelName(backendResp.model_used, model),
                    used_fallback: backendResp.used_fallback ?? false,
                    routed_by: backendResp.routed_by ?? "rules",
                    redirect_path: backendResp.redirect_path || mappedRedirectPath,
                    action: backendResp.action,
                  },
                },
              ]);
              setIsTyping(false);
      
              if (backendResp.is_distress && distressCallbackRef.current) {
                distressCallbackRef.current();
              }
        return;
      }
    } catch (err) {
      console.warn("Backend connection error, falling back to local engine:", err);
    }

    // 2. Fallback to local institutional engine and Database Knowledge Base if backend offline
    setTimeout(async () => {
      let dbSearch: any = null;
      try {
        dbSearch = await askAiKnowledgeBase(query);
      } catch (e) {
        console.warn("Error calling askAiKnowledgeBase Server Action:", e);
      }
      
      if (dbSearch && dbSearch.success && dbSearch.answer) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: dbSearch.answer as string,
            responseMeta: {
              text: dbSearch.answer as string,
              category: (dbSearch.category as QueryCategory) || "INSTITUTIONAL_INFO",
              sourceAgent: dbSearch.source as string || "VIGBOT (Knowledge Base)",
              authorizedFor: student.id,
              isDistress: false,
              llm_provider: "local",
              model_used: "Database Knowledge Base",
              used_fallback: true,
              routed_by: "rules",
            },
          },
        ]);
        setIsTyping(false);
        return;
      }

      const response = processQuery(query, newHistory, activeContextSubject, studentData);
      if (response.contextSubject) {
        setActiveContextSubject(response.contextSubject);
      }

      const localCategoryStr = (response.category as string) || "PERSONAL_DATA";
      let localMappedRedirectPath: string | undefined = undefined;
      
      const qLowerLocal = query.toLowerCase();
      if (localCategoryStr === "ATTENDANCE" || qLowerLocal.includes("attendance")) localMappedRedirectPath = "attendance";
      else if (localCategoryStr === "EXAMS" || qLowerLocal.includes("exam")) localMappedRedirectPath = "exams";
      else if (localCategoryStr === "FEES" || qLowerLocal.includes("fee")) localMappedRedirectPath = "fees";
      else if (localCategoryStr === "TIMETABLE" || qLowerLocal.includes("timetable") || qLowerLocal.includes("schedule")) localMappedRedirectPath = "timetable";
      else if (localCategoryStr === "MARKS" || qLowerLocal.includes("mark") || qLowerLocal.includes("score") || qLowerLocal.includes("grade") || qLowerLocal.includes("cgpa")) localMappedRedirectPath = "marks";
      else if (localCategoryStr === "CURRICULUM" || qLowerLocal.includes("curriculum") || qLowerLocal.includes("credit")) localMappedRedirectPath = "curriculum";
      else if (localCategoryStr === "FACULTY" || qLowerLocal.includes("faculty") || qLowerLocal.includes("teacher") || qLowerLocal.includes("mentor")) localMappedRedirectPath = "faculty";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.text,
          responseMeta: {
            ...response,
            sourceAgent: "VIGBOT [Deterministic Institution Rules]",
            llm_provider: "local",
            model_used: "Rules Engine Only",
            used_fallback: true,
            routed_by: "rules",
            redirect_path: localMappedRedirectPath,
          },
        },
      ]);
      setIsTyping(false);

      // If distress detected, trigger the global supportive mode
      if (response.isDistress && distressCallbackRef.current) {
        distressCallbackRef.current();
      }
    }, 600);
  };

  const handleSpeechToggle = async () => {
    if (typeof window === "undefined") return;

    if (isListening) {
      stopListening();
      return;
    }

    const SpeechRecognition =
      (window as unknown as WindowWithSpeech).SpeechRecognition || (window as unknown as WindowWithSpeech).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert(
        language === "hi"
          ? "आपके ब्राउज़र में स्पीच रिकग्निशन समर्थित नहीं है। कृपया Google Chrome, Microsoft Edge या Brave का उपयोग करें।"
          : language === "te"
          ? "ఈ బ్రౌజర్‌లో స్పీచ్ రికగ్నిషన్ అందుబాటులో లేదు. దయచేసి Google Chrome, Microsoft Edge లేదా Brave వాడండి."
          : "Speech recognition is not supported in this browser. Please use Google Chrome, Microsoft Edge, or Brave."
      );
      return;
    }

    // 1. Explicitly prompt & acquire microphone hardware permission
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
    } catch (err: unknown) {
      console.warn("[VIGBOT Speech] Microphone access denied or not found:", err);
      alert(
        language === "hi"
          ? "माइक्रोफ़ोन अनुमति नहीं मिली। कृपया ब्राउज़र URL बार में माइक आइकॉन पर क्लिक करके 'Allow' करें।"
          : language === "te"
          ? "మైక్రోఫోన్ అనుమతి లభించలేదు. దయచేసి బ్రౌజర్ URL బార్‌లో మైక్ చిహ్నాన్ని క్లిక్ చేసి 'Allow' చేయండి."
          : "Microphone access was denied. Please allow microphone access in your browser address bar."
      );
      return;
    }

    // 2. Initialize Continuous Speech Recognition
    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.continuous = true; // Stay active; do not mute on short pauses
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      // Select high-accuracy Indian language acoustic models
      if (language === "te") {
        recognition.lang = "te-IN";
      } else if (language === "hi") {
        recognition.lang = "hi-IN";
      } else {
        recognition.lang = "en-IN";
      }

      // 15-second total timeout if no speech at all
      silenceTimerRef.current = setTimeout(() => {
        stopListening();
      }, 15000);

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        // Reset timer on receiving speech
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current);
        }
        // Auto-stop 3.5s after student finishes speaking
        silenceTimerRef.current = setTimeout(() => {
          stopListening();
        }, 3500);

        let finalTranscript = "";
        let interimTranscript = "";
        for (let i = 0; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript + " ";
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        const text = (finalTranscript + interimTranscript).trim();
        if (text) {
          setInputQuery(text);
        }
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.warn("[VIGBOT Speech] Recognition event error:", event.error);

        // DO NOT stop on "no-speech" — student is just pausing before speaking
        if (event.error === "no-speech") {
          return;
        }

        stopListening();

        if (event.error === "network") {
          alert(
            language === "hi"
              ? "Brave Browser में स्पीच सर्विस बाय-डिफ़ॉल्ट बंद होती है।\n\nइसे चालू करने के लिए:\n1. नए टैब में brave://settings/privacy खोलें\n2. 'Use Google services for speech recognition' को ON करें\n3. इस पेज को रिफ्रेश करें और माइक इस्तेमाल करें!\n(या फिर Google Chrome / Edge में चलाएं)"
              : language === "te"
              ? "Brave Browser లో స్పీచ్ సర్వీస్ డిఫాల్ట్‌గా ఆఫ్ చేయబడింది.\n\nఆన్ చేయడానికి:\n1. కొత్త ట్యాబ్‌లో brave://settings/privacy తెరవండి\n2. 'Use Google services for speech recognition' ఆన్ చేయండి\n(లేదా Google Chrome / Edge వాడండి)"
              : "Brave Browser blocks Google speech recognition by default for privacy.\n\nTo enable speech in Brave:\n1. Open a new tab and go to: brave://settings/privacy\n2. Turn ON 'Use Google services for speech recognition'\n3. Refresh this page and click the mic again!\n(Alternatively, use Google Chrome or Microsoft Edge)"
          );
        } else if (event.error === "not-allowed" || event.error === "service-not-allowed") {
          alert(
            language === "hi"
              ? "माइक्रोफ़ोन अनुमति अवरुद्ध है। कृपया ब्राउज़र URL बार में माइक आइकॉन पर क्लिक करके 'Allow' करें।"
              : language === "te"
              ? "మైక్రోఫోన్ అనుమతి నిరోధించబడింది. దయచేసి బ్రౌజర్ URL బార్‌లో మైక్ చిహ్నాన్ని క్లిక్ చేసి 'Allow' చేయండి."
              : "Microphone permission is blocked. Please click the mic/lock icon in your browser URL bar and allow microphone access."
          );
        }
      };

      recognition.onend = () => {
        stopListening();
      };

      recognition.start();
    } catch (err) {
      console.error("[VIGBOT Speech] Failed to start speech recognition:", err);
      stopListening();
    }
  };

  const handleResetChat = () => {
    setMessages([buildInitialGreeting(student, language)]);
  };

  // Keyboard shortcut listener for ESC to close maximize mode
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isMaximized) {
        setIsMaximized(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isMaximized]);

  return (
    <AgentChatContext.Provider
      value={{
        messages,
        inputQuery,
        setInputQuery,
        isTyping,
        isListening,
        isMaximized,
        setIsMaximized,
        activeContextSubject,
        handleSend,
        handleResetChat,
        handleSpeechToggle,
        registerDistressCallback,
      }}
    >
      {children}
    </AgentChatContext.Provider>
  );
};

export const useAgentChat = () => {
  const context = useContext(AgentChatContext);
  if (!context) {
    throw new Error("useAgentChat must be used within an AgentChatProvider");
  }
  return context;
};
