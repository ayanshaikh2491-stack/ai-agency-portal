import { NextResponse } from "next/server";
import Groq from "groq-sdk";

const client = new Groq({ apiKey: process.env.GROQ_API_KEY });
const MODEL = process.env.GROQ_MODEL || "llama-3.1-8b-instant";

const DEPT_PROMPTS = {
  web: "You are the Web Department of an AI Agency. You help with website development, frontend, backend, API, deployment, and web-related tasks. Respond helpfully and concisely.",
  seo: "You are the SEO Department of an AI Agency. You help with search engine optimization, Google ranking, analytics, and growth tracking. Respond helpfully.",
  marketing: "You are the Marketing Department of an AI Agency. You help with digital marketing, ads, campaigns, email marketing, and funnels. Respond helpfully.",
  social_media: "You are the Social Media Department. You help with content creation, social media management, posts, and reels. Respond helpfully.",
};

export async function POST(req) {
  try {
    const body = await req.json();
    const message = body.message || "";
    const department = body.department || "web";
    const history = body.history || [];

    if (!message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    const systemPrompt = DEPT_PROMPTS[department] || DEPT_PROMPTS.web;

    const messages = [
      { role: "system", content: systemPrompt },
      ...history.map((m) => ({ role: m.role, content: m.content })),
      { role: "user", content: message },
    ];

    const completion = await client.chat.completions.create({
      model: MODEL,
      messages,
      temperature: 0.7,
      max_tokens: 1024,
    });

    const reply = completion.choices[0]?.message?.content || "Sorry, I couldn't generate a response.";

    return NextResponse.json({ response: reply, sender: `${department} Department` });
  } catch (error) {
    console.error("Dept Chat Error:", error);
    return NextResponse.json(
      { error: error.message || "Internal server error", response: "Error: Could not connect to AI service.", sender: "System" },
      { status: 500 }
    );
  }
}