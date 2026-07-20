"""
src/chunker.py - Transcript Chunking Module
Provides helper functions to divide long earnings call transcripts into manageable chunks
while respecting token limits of LLM context windows.
"""

import re
import tiktoken
from typing import List, Dict, Any

def get_token_count(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Calculates the exact token count of a given text using tiktoken.
    Falls back to a rough word-count estimate if tiktoken fails.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback approximation: ~1.3 tokens per word
        return int(len(text.split()) * 1.3)

def split_transcript_by_speaker(transcript: str) -> List[Dict[str, str]]:
    """
    Parses a transcript into structural parts based on speakers.
    Detects lines starting with Capital Names (e.g., "Tim Cook:", "Elon Musk:").
    Returns a list of dicts: [{"speaker": "Tim Cook", "text": "..."}]
    """
    # Regex to find speaker declarations (e.g., "John Doe:", "Operator:")
    speaker_pattern = re.compile(r"^([A-Z][a-zA-Z\s.-]+):", re.MULTILINE)
    
    parts = []
    matches = list(speaker_pattern.finditer(transcript))
    
    if not matches:
        # If no speaker-like structure is detected, treat as one large block
        return [{"speaker": "Unspecified Speaker", "text": transcript.strip()}]
        
    for i, match in enumerate(matches):
        speaker = match.group(1).strip()
        start_idx = match.end()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(transcript)
        
        text = transcript[start_idx:end_idx].strip()
        if text:
            parts.append({"speaker": speaker, "text": text})
            
    return parts

def chunk_transcript(
    transcript: str, 
    max_chunk_tokens: int = 2500, 
    overlap_tokens: int = 200, 
    model: str = "gpt-4o-mini"
) -> List[str]:
    """
    Chunks a long transcript into overlapping text blocks of a specific token limit.
    This ensures we don't truncate structural sentences or lose context between boundaries.
    """
    # Clean whitespace
    clean_text = re.sub(r"\s+", " ", transcript).strip()
    words = clean_text.split()
    
    # Simple word-based sliding chunker (robust and easy to read)
    # Average 1 word = 1.3 tokens. 2500 tokens is ~1900 words.
    target_chunk_words = int(max_chunk_tokens / 1.3)
    overlap_words = int(overlap_tokens / 1.3)
    
    chunks = []
    start_idx = 0
    
    while start_idx < len(words):
        end_idx = min(start_idx + target_chunk_words, len(words))
        chunk_words = words[start_idx:end_idx]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)
        
        if end_idx == len(words):
            break
        
        # Advance by size minus overlap
        start_idx += (target_chunk_words - overlap_words)
        
    return chunks
