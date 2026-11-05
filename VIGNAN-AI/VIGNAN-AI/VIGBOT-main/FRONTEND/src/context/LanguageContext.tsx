"use client";

import React, { createContext, useContext, useState } from "react";
import { Language, TranslationDictionary, TRANSLATIONS, tDynamic as tDynamicHelper } from "@/data/translations";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: TranslationDictionary;
  tDynamic: (text: string | null | undefined) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    if (typeof window !== "undefined") {
      const savedLang = (localStorage.getItem("vigbot_lang") || localStorage.getItem("agent65_lang")) as Language;
      if (savedLang && savedLang in TRANSLATIONS) {
        return savedLang;
      }
    }
    return "en";
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    if (typeof window !== "undefined") {
      localStorage.setItem("vigbot_lang", lang);
    }
  };

  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  const tDynamic = (text: string | null | undefined) => tDynamicHelper(text, language);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, tDynamic }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    return {
      language: "en",
      setLanguage: () => { },
      t: TRANSLATIONS.en,
      tDynamic: (text) => tDynamicHelper(text, "en"),
    };
  }
  return context;
};
