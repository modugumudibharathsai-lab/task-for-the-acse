"use server";

import { getDb } from "../lib/db-provider";



export async function askAiKnowledgeBase(query: string) {
  try {
    const db = getDb();
    
    // Very simple keyword matching for demonstration purposes.
    const normalizedQuery = query.toLowerCase();
    const faqs = db.prepare('SELECT * FROM ai_knowledge_base').all();

    let bestMatch = null;
    let maxMatches = 0;

    for (const faq of faqs) {
      let matches = 0;
      const questionWords = (faq as any).question.toLowerCase().split(' ');
      
      // Check tags in metadata
      let tags = [];
      try {
        const meta = JSON.parse((faq as any).metadata);
        if (meta.tags) tags = meta.tags;
      } catch (e) {}

      // Match logic
      const searchTerms = [...questionWords, ...tags];
      for (const term of searchTerms) {
        if (term.length > 3 && normalizedQuery.includes(term.toLowerCase())) {
          matches++;
        }
      }

      // Also check exact category matches
      if (normalizedQuery.includes((faq as any).category.toLowerCase())) {
          matches += 2;
      }

      if (matches > maxMatches) {
        maxMatches = matches;
        bestMatch = faq;
      }
    }

    if (bestMatch && maxMatches > 0) {
      return { 
          success: true, 
          answer: (bestMatch as any).answer, 
          category: (bestMatch as any).category,
          source: "VIGBOT (Knowledge Base Database)"
      };
    }
    
    return { success: false, answer: null };

  } catch (error: any) {
    console.error("AI Search Error:", error);
    return { success: false, error: error.message };
  }
}
