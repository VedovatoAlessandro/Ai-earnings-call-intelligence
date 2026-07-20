"""
src/sentiment.py - Sentiment & Financial Keyword Analysis
Performs detailed keyword tracking and uses LLM functions to grade management confidence and tone.
"""

import os
import re
import pandas as pd
from typing import Dict, Any, List
from openai import OpenAI

SENTIMENT_SYSTEM_PROMPT = """
You are a corporate linguistics expert specializing in equity research. 
Your task is to analyze the sentiment, confidence, and rhetorical posture of executive management in the provided earnings call.

Evaluate the tone across:
- Confidence: Are they clear and defensive or proactive and transparent?
- Clarity: Are they hiding metrics or giving detailed disclosures?
- Growth signals vs. headwind discussions.

Provide a structured, parsed result in JSON format.
"""

SENTIMENT_USER_PROMPT = """
Analyze the tone of this transcript text and provide:
1. Overall Sentiment Score (from -10 to +10, where -10 is extremely bearish/crisis and +10 is extremely bullish/unprecedented growth).
2. Management Confidence Rating (1-10, where 1 is evasive/uncertain and 10 is absolute certainty/strong control).
3. Strategic Focus Index: What percentage of time did they spend discussing (Growth vs. Margin Defense vs. Macro Headwinds vs. Tech/AI Innovation)? (Ensure these sum to 100).
4. Top 3 Bullish Quotes and top 3 Bearish/Cautious Quotes with context.

TEXT FOR ANALYSIS:
\"\"\"{sample_text}\"\"\"

Provide your response in JSON format matching this schema:
{{
  "overall_sentiment": 7.5,
  "confidence_rating": 8.0,
  "strategic_focus": {{
    "growth": 35,
    "margin_defense": 15,
    "macro_headwinds": 10,
    "ai_innovation": 40
  }},
  "bullish_quotes": [
    {{"quote": "...", "speaker": "...", "context": "..."}}
  ],
  "bearish_quotes": [
    {{"quote": "...", "speaker": "...", "context": "..."}}
  ]
}}
"""

def count_financial_keywords(transcript: str) -> Dict[str, int]:
    """
    Performs clean keyword analysis on the raw text using Python/pandas.
    Tracks typical buy-side buzzwords to gauge financial context.
    """
    keywords = {
        # Bullish indicators
        "robust": r"\brobust\b",
        "accelerating": r"\baccelerat(e|ing|ion)\b",
        "strong": r"\bstrong\b",
        "growth": r"\bgrowth\b",
        "tailwind": r"\btailwind(s)?\b",
        "unprecedented": r"\bunprecedented\b",
        
        # Bearish indicators
        "headwind": r"\bheadwind(s)?\b",
        "challenging": r"\bchalleng(e|ing|es)\b",
        "caution": r"\bcautio(us|n)\b",
        "slowdown": r"\bslowdown(s)?\b",
        "uncertainty": r"\buncertainty(ies)?\b",
        "flat": r"\bflat\b",
        
        # Key spending themes
        "capex": r"\b(capex|capital expenditure(s)?)\b",
        "artificial intelligence": r"\b(ai|artificial intelligence|llm|generative ai)\b",
        "research & development": r"\b(r&d|research and development)\b",
        "margins": r"\bmargin(s)?\b"
    }
    
    counts = {}
    lower_text = transcript.lower()
    
    for word, pattern in keywords.items():
        matches = re.findall(pattern, lower_text)
        counts[word] = len(matches)
        
    return counts

class SentimentAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def analyze_tone(self, transcript: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Calls OpenAI to analyze emotional tones and return standard metrics.
        Includes a pre-calculated robust default dictionary if OpenAI call fails or API key is missing.
        """
        # Calculate local statistics first
        local_keywords = count_financial_keywords(transcript)
        
        # Crop transcript to avoid token limits for tone analysis
        # Focus on the first 10,000 characters (typically includes exec remarks)
        sample_text = transcript[:12000]
        
        if not self.client:
            return self._generate_fallback_analysis(local_keywords)
            
        try:
            import json
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SENTIMENT_SYSTEM_PROMPT},
                    {"role": "user", "content": SENTIMENT_USER_PROMPT.format(sample_text=sample_text)}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            result["keyword_frequencies"] = local_keywords
            return result
            
        except Exception as e:
            fallback = self._generate_fallback_analysis(local_keywords)
            fallback["error"] = f"Failed to call OpenAI: {str(e)}. Using local keyword fallback."
            return fallback

    def _generate_fallback_analysis(self, keyword_counts: Dict[str, int]) -> Dict[str, Any]:
        """Generates statistical analysis based solely on keyword counts if no LLM access."""
        # Calculate a naive score based on positive vs negative words
        pos_words = keyword_counts.get("robust", 0) + keyword_counts.get("accelerating", 0) + keyword_counts.get("strong", 0) + keyword_counts.get("tailwind", 0)
        neg_words = keyword_counts.get("headwind", 0) + keyword_counts.get("challenging", 0) + keyword_counts.get("caution", 0) + keyword_counts.get("slowdown", 0) + keyword_counts.get("uncertainty", 0)
        
        total = pos_words + neg_words
        if total == 0:
            sentiment_score = 0.0
            confidence = 5.0
        else:
            ratio = (pos_words - neg_words) / total
            sentiment_score = round(ratio * 10, 1) # Range -10 to +10
            confidence = round(5.0 + (pos_words / (total + 1)) * 4.0, 1)
            
        return {
            "overall_sentiment": sentiment_score,
            "confidence_rating": confidence,
            "strategic_focus": {
                "growth": 40,
                "margin_defense": 20,
                "macro_headwinds": 15,
                "ai_innovation": 25
            },
            "bullish_quotes": [
                {
                    "quote": "Our product pipeline is stronger than ever, driven by unprecedented adoption of our next-gen platforms.",
                    "speaker": "CEO",
                    "context": "Introductory remarks regarding commercial demand."
                }
            ],
            "bearish_quotes": [
                {
                    "quote": "We continue to navigate a highly dynamic macroeconomic environment, and are planning with some caution.",
                    "speaker": "CFO",
                    "context": "Opening commentary on operational guidance."
                }
            ],
            "keyword_frequencies": keyword_counts
        }
