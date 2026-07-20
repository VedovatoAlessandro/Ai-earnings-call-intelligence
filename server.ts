import express from "express";
import path from "path";
import dotenv from "dotenv";
import { GoogleGenAI, Type } from "@google/genai";
import { createServer as createViteServer } from "vite";

// Load environment variables
dotenv.config();

const app = express();
app.use(express.json({ limit: "10mb" })); // Support large transcript files

const PORT = 3000;

// Initialize Gemini SDK with telemetry header
const ai = process.env.GEMINI_API_KEY
  ? new GoogleGenAI({
      apiKey: process.env.GEMINI_API_KEY,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build",
        },
      },
    })
  : null;

// Local word counting logic (mimics Python's pandas/regex counts)
function countFinancialKeywords(transcript: string) {
  const keywords: Record<string, RegExp> = {
    "robust": /\brobust\b/gi,
    "accelerating": /\baccelerat(e|ing|ion)\b/gi,
    "strong": /\bstrong\b/gi,
    "growth": /\bgrowth\b/gi,
    "tailwind": /\btailwind(s)?\b/gi,
    "unprecedented": /\bunprecedented\b/gi,
    "headwind": /\bheadwind(s)?\b/gi,
    "challenging": /\bchalleng(e|ing|es)\b/gi,
    "caution": /\bcautio(us|n)\b/gi,
    "slowdown": /\bslowdown(s)?\b/gi,
    "uncertainty": /\buncertainty(ies)?\b/gi,
    "flat": /\bflat\b/gi,
    "capex": /\b(capex|capital expenditure(s)?)\b/gi,
    "artificial intelligence": /\b(ai|artificial intelligence|llm|generative ai)\b/gi,
    "research & development": /\b(r&d|research and development)\b/gi,
    "margins": /\bmargin(s)?\b/gi,
  };

  const counts: Record<string, number> = {};
  for (const [key, regex] of Object.entries(keywords)) {
    const matches = transcript.match(regex);
    counts[key] = matches ? matches.length : 0;
  }
  return counts;
}

// -------------------------------------------------------------
// FULL-STACK SERVER ENDPOINTS
// -------------------------------------------------------------

// API Health Check
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", geminiConfigured: !!ai });
});

// Live Ingestion and Summarization Endpoint
app.post("/api/summarize", async (req, res) => {
  const { transcript, companyName } = req.body;

  if (!transcript || transcript.trim().length === 0) {
    return res.status(400).json({ error: "Transcript content is required." });
  }

  // Calculate local keywords
  const keyword_frequencies = countFinancialKeywords(transcript);

  // If Gemini API is not configured, send a helpful fallback mock response that simulates the output
  if (!ai) {
    console.log("Gemini API key is not configured. Returning local fallback mock analysis.");
    return res.json({
      summary: `### 1. Executive Summary
The earnings call for **${companyName || "Portfolio Company"}** highlights a transitional period marked by solid core demand in primary business segments, countered by emerging macroeconomic pressures. Management is focused on capital discipline and long-term tech scaling.

### 2. Bull Case & Key Catalysts (Opportunities)
- **Accelerating Core Demand**: Customer expansion continues to drive substantial top-line momentum, supporting a strong **8% revenue expansion** in key product lines.
- **R&D Breakthroughs**: Investment in artificial intelligence remains a key pillar of long-term value, leading to **unprecedented early adoption** of their digital pilot suites.
- **Operational Liquidity**: Robust free cash flows of **$2.4B** support active share repurchases and long-term financial security.

### 3. Bear Case & Structural Risks
- **Macro Headwinds**: Rising inflation and supply chain frictions introduce noticeable margin pressure, leading to conservative near-term guidance.
- **Slowing Hardware Channels**: Traditional channels are showing a minor **slowdown** as consumer spend pivots towards software-enabled services.
- **Geopolitical Risks**: Cross-border logistical hurdles represent an ongoing operational risk factor.

### 4. Financial Guidance & Capital Allocation
- **Top-Line Guidance**: Management projects full-year revenue to hit between **$14.2B and $14.5B**, representing a mild deceleration but remaining highly resilient.
- **Capex Forecast**: Total capital expenditure is projected at **$1.8B** to support AI processing farms and physical warehouses.
- **Dividends & Buybacks**: Board authorized an additional **$500M** stock buyback program, reinforcing commitment to shareholder returns.

### 5. Dynamic Guidance Table
| Metric | Previous Range/Estimate | New Guidance/Range | Commentary |
| :--- | :--- | :--- | :--- |
| **Revenue** | $14.0B - $14.3B | $14.2B - $14.5B | Supported by digital service momentum |
| **Gross Margin** | 42.5% | 41.8% - 42.2% | Dampened by short-term supply chain headwinds |
| **Capex** | $1.5B | $1.8B | Heavy scaling on artificial intelligence server farms |
| **Free Cash Flow** | $2.0B | $2.2B | Driven by working capital optimizations |`,
      overall_sentiment: 4.8,
      confidence_rating: 7.2,
      strategic_focus: {
        growth: 40,
        margin_defense: 25,
        macro_headwinds: 20,
        ai_innovation: 15,
      },
      bullish_quotes: [
        {
          quote: "Our operational foundation is incredibly robust, allowing us to capture secular software tailwinds.",
          speaker: "CEO",
          context: "Introductory executive address to buy-side analysts.",
        },
        {
          quote: "We are seeing accelerating customer pipelines for our next-generation cloud services.",
          speaker: "Head of Cloud",
          context: "QA session answering general tech backlog questions.",
        },
      ],
      bearish_quotes: [
        {
          quote: "We must operate with caution given the persistent headwind in our European shipping lanes.",
          speaker: "CFO",
          context: "Segment overview of logistical margins.",
        },
        {
          quote: "A short-term slowdown in consumer electronics may pressure hardware volumes slightly.",
          speaker: "COO",
          context: "Segment breakdown of hardware shipments.",
        },
      ],
      keyword_frequencies,
      simulated: true,
    });
  }

  try {
    const prompt = `
    Analyze the following earnings call transcript for the company: "${companyName || "Unspecified Company"}".
    You must extract and synthesize corporate performance, guidelines, tones, and metrics.
    
    TRANSCRIPT TEXT:
    """
    ${transcript}
    """
    `;

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: prompt,
      config: {
        systemInstruction: `
        You are a seasoned Wall Street equity research analyst. 
        Your task is to analyze the provided earnings call transcript and output structured, institutional-grade quantitative insights.
        Focus heavily on hard numbers, margin percentages, Capex ranges, and management linguistic postures.
        You MUST provide your response strictly in the requested JSON structure.
        `,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            summary: {
              type: Type.STRING,
              description: `Pristine Markdown investor memo report. MUST include these exact sections:
### 1. Executive Summary
- A 3-4 sentence high-level overview of the company's quarter, primary growth drivers, and overall health.

### 2. Bull Case & Key Catalysts (Opportunities)
- 4-5 bullet points focusing on bullish developments, demand expansion, margin tailwinds, or product successes. Use bold for key numbers/metrics.

### 3. Bear Case & Structural Risks
- 4-5 bullet points highlighting bearish indicators, demand slowdown, margin pressures, supply chain issues, or competitive threats.

### 4. Financial Guidance & Capital Allocation
- Detailed breakdown of revenue guidance, margin outlook, Capex guidance (especially AI/infrastructure spending), and capital return initiatives (buybacks/dividends).

### 5. Dynamic Guidance Table
- Provide a summary of guidance changes in a markdown table format with columns: [Metric, Previous Range/Estimate, New Guidance/Range, Commentary].`,
            },
            overall_sentiment: {
              type: Type.NUMBER,
              description: "Management sentiment score from -10 (highly bearish) to +10 (highly bullish).",
            },
            confidence_rating: {
              type: Type.NUMBER,
              description: "Management confidence rating from 1 to 10 based on clarity and directness.",
            },
            strategic_focus: {
              type: Type.OBJECT,
              properties: {
                growth: { type: Type.NUMBER, description: "Percentage of discussion on Growth (0-100)" },
                margin_defense: { type: Type.NUMBER, description: "Percentage of discussion on Margin Defense (0-100)" },
                macro_headwinds: { type: Type.NUMBER, description: "Percentage of discussion on Macro Headwinds (0-100)" },
                ai_innovation: { type: Type.NUMBER, description: "Percentage of discussion on AI / Technology Innovation (0-100)" },
              },
              required: ["growth", "margin_defense", "macro_headwinds", "ai_innovation"],
            },
            bullish_quotes: {
              type: Type.ARRAY,
              description: "List of top 2-3 bullish quotes from the call.",
              items: {
                type: Type.OBJECT,
                properties: {
                  quote: { type: Type.STRING },
                  speaker: { type: Type.STRING },
                  context: { type: Type.STRING },
                },
                required: ["quote", "speaker", "context"],
              },
            },
            bearish_quotes: {
              type: Type.ARRAY,
              description: "List of top 2-3 cautious or bearish quotes from the call.",
              items: {
                type: Type.OBJECT,
                properties: {
                  quote: { type: Type.STRING },
                  speaker: { type: Type.STRING },
                  context: { type: Type.STRING },
                },
                required: ["quote", "speaker", "context"],
              },
            },
          },
          required: [
            "summary",
            "overall_sentiment",
            "confidence_rating",
            "strategic_focus",
            "bullish_quotes",
            "bearish_quotes",
          ],
        },
      },
    });

    const resultText = response.text;
    if (!resultText) {
      throw new Error("No text returned from Gemini API");
    }

    const result = JSON.parse(resultText);
    result.keyword_frequencies = keyword_frequencies;
    result.simulated = false;

    res.json(result);
  } catch (error: any) {
    console.error("Gemini Ingestion Pipeline error:", error);
    res.status(500).json({
      error: "Failed to run transcript analysis through Gemini.",
      details: error.message || String(error),
    });
  }
});

// -------------------------------------------------------------
// VITE CLIENT-SERVER ROUTING INTERACTION
// -------------------------------------------------------------
async function bootstrap() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server successfully booted and listening on http://localhost:${PORT}`);
  });
}

bootstrap();
