import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());

// Serving the static frontend folder
const frontendDir = path.join(__dirname, "frontend");
app.use(express.static(frontendDir));

// Initialize Gemini Client
let ai = null;
if (process.env.GEMINI_API_KEY) {
  try {
    ai = new GoogleGenAI({
      apiKey: process.env.GEMINI_API_KEY,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build"
        }
      }
    });
    console.log("❇️ Gemini client initialized successfully.");
  } catch (err) {
    console.error("⚠️ Failed to initialize Gemini client:", err);
  }
} else {
  console.log("ℹ️ GEMINI_API_KEY not found. Operating with local fallback rule-based system.");
}

// System endpoints
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    gemini_enabled: !!ai,
    environment: process.env.NODE_ENV || "development"
  });
});

// Backward compatibility or API namespace
app.get("/api/health", (req, res) => {
  res.json({ status: "healthy", gemini_enabled: !!ai });
});

// Predict malaria risk endpoint
app.post("/predict", async (req, res) => {
  try {
    const {
      age,
      gender,
      state,
      lga,
      symptoms,
      duration,
      mosquitoBites,
      travelled,
      malariaDrugs
    } = req.body;

    // Validate request inputs
    if (age === undefined || !gender || !state || !symptoms) {
      return res.status(400).json({
        error: "Missing required fields: age, gender, state, and symptoms are required."
      });
    }

    // Heuristic Clinical Scoring
    let score = 0;
    const symptomsList = Array.isArray(symptoms) ? symptoms : [];

    if (symptomsList.includes("High Fever")) {
      score += 3.5;
    } else if (symptomsList.includes("Fever")) {
      score += 2.0;
    }

    if (symptomsList.includes("Chills")) score += 1.5;
    if (symptomsList.includes("Vomiting")) score += 1.5;
    if (symptomsList.includes("Headache")) score += 1.0;
    if (symptomsList.includes("Fatigue")) score += 0.5;
    if (symptomsList.includes("Body Pain")) score += 0.5;
    if (symptomsList.includes("Loss of Appetite")) score += 0.5;
    if (symptomsList.includes("Sweating")) score += 0.5;

    if (mosquitoBites) score += 2.0;
    if (travelled) score += 1.5;

    // Compute base probability
    let probability = 0.05 + (score / 12) * 0.90;

    // Adjustments for medications
    if (malariaDrugs) {
      probability = Math.max(0.1, probability - 0.15); // Treated, but vigilance is high
    }

    probability = Math.max(0.05, Math.min(0.98, probability));

    // Determine Urgency Level
    let urgency = "Low";
    if (probability >= 0.70) {
      urgency = "High";
    } else if (probability >= 0.30) {
      urgency = "Medium";
    }

    const prediction = probability >= 0.50 ? "Malaria" : "No Malaria";

    // Set fallback insights and recommendations
    let aiInsightsText = "";
    let recommendation = "";

    const fallbackRecommendation = urgency === "High"
      ? "Visit the nearest health facility immediately. This tool is for screening only and is not a medical diagnosis. A doctor should perform a blood film microscopy or Rapid Diagnostic Test (RDT) to confirm malaria."
      : urgency === "Medium"
      ? "Monitor your symptoms closely and seek medical attention if they worsen. Consider visiting a healthcare provider or a local pharmacy/clinic for an RDT screening."
      : "Current risk appears low. Continue monitoring your symptoms. If symptoms persist or worsen, consult a healthcare provider. Ensure you sleep under a long-lasting insecticidal net (LLIN).";

    const fallbackInsightsText = `The patient is a ${age}-year-old ${gender} in ${state}, Nigeria presenting with symptoms (${symptomsList.join(", ")}) for ${duration} days. Based on clinical symptom triage parameters, the estimated risk probability is ${Math.round(probability * 100)}%, placing them in the ${urgency} risk category. Malaria transmission is endemic throughout Nigeria, so any fever symptoms should be monitored with extreme care.`;

    if (ai) {
      try {
        const prompt = `You are an expert AI clinical triage advisor specializing in tropical medicine and infectious diseases in Nigeria.
You are evaluating a patient's malaria risk based on their symptoms and exposure context:
- Age: ${age} years
- Gender: ${gender}
- Location: ${state}, Nigeria ${lga ? `(LGA: ${lga})` : ""}
- Reported Symptoms: ${symptomsList.join(", ")}
- Symptom Duration: ${duration} days
- Recent mosquito bites: ${mosquitoBites ? "Yes" : "No"}
- Travelled recently to malaria-endemic/rural area: ${travelled ? "Yes" : "No"}
- Taken malaria drugs recently: ${malariaDrugs ? "Yes" : "No"}

We have calculated a baseline statistical risk probability of ${Math.round(probability * 100)}% which places this patient in the "${urgency}" triage urgency category.

Please generate a professional, highly clear, and empathetic clinical analysis in JSON format matching the following schema:
{
  "insights": "A 1-2 paragraph detailed clinical analysis of the symptoms, explaining how the presented symptoms (especially the presence or absence of fever, chills, vomiting, etc.) correlate with malaria risk. Reference the specific geographical context of ${state}, Nigeria and general malaria guidelines. Be objective, realistic, and highly educational.",
  "recommendation": "Clear, bulleted clinical recommendations for what the patient should do next (e.g., visit a clinic for a malaria test - microscopy/RDT, rest, hydration, monitoring for emergency signs like severe headache, confusion, or dark urine)."
}

IMPORTANT: Do not make a formal medical diagnosis. Remind the patient that this is a screening tool. Ensure the output is valid JSON.`;

        const response = await ai.models.generateContent({
          model: "gemini-3.5-flash",
          contents: prompt,
          config: {
            responseMimeType: "application/json"
          }
        });

        const resData = JSON.parse(response.text);
        aiInsightsText = resData.insights || fallbackInsightsText;
        recommendation = resData.recommendation || fallbackRecommendation;
      } catch (err) {
        console.error("⚠️ Gemini API execution error, falling back to local text:", err);
        aiInsightsText = fallbackInsightsText;
        recommendation = fallbackRecommendation;
      }
    } else {
      aiInsightsText = fallbackInsightsText;
      recommendation = fallbackRecommendation;
    }

    res.json({
      prediction,
      probability: parseFloat(probability.toFixed(4)),
      urgency,
      recommendation,
      aiInsights: aiInsightsText
    });

  } catch (error) {
    console.error("Prediction endpoint failed:", error);
    res.status(500).json({ error: "Internal server error during prediction." });
  }
});

// Fallback all unspecified routes to the login page (or main entry point)
app.get("*", (req, res) => {
  res.sendFile(path.join(frontendDir, "login.html"));
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
