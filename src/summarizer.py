"""
src/summarizer.py - OpenAI Summarization Pipeline
Implements the core LLM pipeline for processing transcripts and generating high-quality financial insights.
"""

import os
from openai import OpenAI
from typing import List, Dict, Any
from src.chunker import chunk_transcript

# Define our highly-optimized financial system prompts
FINANCIAL_SYSTEM_PROMPT = """
You are an expert Wall Street buy-side equity research analyst and fintech product manager. 
Your job is to read earnings call transcripts and extract rigorous, objective, and quantitative insights. 

Avoid generic corporate buzzwords or vague summaries. Focus on:
1. Hard quantitative metrics (revenue growth, margin expansion/contraction, guidance ranges, capex, backlog).
2. Management's tone and changes in vocabulary (e.g., shifts from 'securing demand' to 'navigating headwind').
3. Discrepancies between historical performance and future expectations.
4. Capital allocation choices (buybacks, dividends, debt repayment, R&D, and Capex).

Deliver output in pristine, highly structured Markdown formats, utilizing bullet points with bold metrics where applicable.
"""

MAP_PROMPT_TEMPLATE = """
Analyze the following chunk of an earnings call transcript (Part {part_num} of {total_parts}). 
Extract the primary details regarding:
- Key financial results or guidance mentioned.
- Strategic initiatives discussed (especially AI, R&D, product pipelines).
- Major risk factors, supply chain, or macroeconomic headwinds.
- Major customer wins, market expansion, or demand signals.

TRANSCRIPT CHUNK:
\"\"\"{chunk_text}\"\"\"

Provide bullet points of your findings below. Make them precise and mention actual numbers wherever they are mentioned.
"""

REDUCE_PROMPT_TEMPLATE = """
You are a senior investment analyst compiling a final investment memo based on several analyzed parts of an earnings call transcript.
Your goal is to synthesize these partial findings into a cohesive, professional Investor Dashboard report.

Below are the summarized findings from various parts of the call:
\"\"\"{summarized_chunks}\"\"\"

Please synthesize this data into a professional financial briefing with the following exact structure:

### 1. Executive Summary
- A concise 3-4 sentence high-level overview of the company's quarter, their primary growth drivers, and overall health.

### 2. Bull Case & Key Catalysts (Opportunities)
- 4-5 bullet points focusing on bullish developments, demand expansion, margin tailwinds, or product successes. Use bold for key numbers/metrics.

### 3. Bear Case & Structural Risks
- 4-5 bullet points highlighting bearish indicators, demand slowdown, margin pressures, supply chain issues, or competitive threats.

### 4. Financial Guidance & Capital Allocation
- Detailed breakdown of revenue guidance, margin outlook, Capex guidance (especially AI/infrastructure spending), and capital return initiatives (buybacks/dividends).

### 5. Dynamic Guidance Table
- Provide a summary of guidance changes in a markdown table format with columns: [Metric, Previous Range/Estimate, New Guidance/Range, Commentary].
"""

class EarningsSummarizer:
    def __init__(self, api_key: str = None):
        # Fallback to env variable if not explicitly passed
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def _call_llm(self, system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
        """Helper to invoke the OpenAI API with robust error handling."""
        if not self.client:
            return "Error: OpenAI API key is missing. Please set your OPENAI_API_KEY."
            
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"API Error calling OpenAI: {str(e)}"

    def summarize(self, transcript: str, model: str = "gpt-4o-mini") -> str:
        """
        Main summarization pipeline. 
        Uses a Map-Reduce approach to handle transcripts of arbitrary length.
        """
        # Step 1: Chunk the transcript
        chunks = chunk_transcript(transcript, max_chunk_tokens=3000, overlap_tokens=300, model=model)
        
        if len(chunks) == 1:
            # Simple single-call summarization if transcript is short enough
            map_findings = chunks[0]
            final_report = self._call_llm(
                system_prompt=FINANCIAL_SYSTEM_PROMPT,
                user_prompt=REDUCE_PROMPT_TEMPLATE.format(summarized_chunks=map_findings),
                model=model
            )
            return final_report
            
        # Step 2: Map phase - Summarize each chunk in parallel or sequence
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            user_prompt = MAP_PROMPT_TEMPLATE.format(
                part_num=i + 1,
                total_parts=len(chunks),
                chunk_text=chunk
            )
            summary = self._call_llm(
                system_prompt=FINANCIAL_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                model=model,
                temperature=0.1
            )
            chunk_summaries.append(f"--- PART {i+1} SUMMARIES ---\n{summary}\n")
            
        # Step 3: Reduce phase - Synthesize chunk summaries into final report
        synthesized_chunks_text = "\n".join(chunk_summaries)
        final_report = self._call_llm(
            system_prompt=FINANCIAL_SYSTEM_PROMPT,
            user_prompt=REDUCE_PROMPT_TEMPLATE.format(summarized_chunks=synthesized_chunks_text),
            model=model,
            temperature=0.2
        )
        
        return final_report
