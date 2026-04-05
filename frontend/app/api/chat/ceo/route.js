import { NextResponse } from "next/server";
import Groq from "groq-sdk";

const client = new Groq({ apiKey: process.env.GROQ_API_KEY });
const MODEL = process.env.GROQ_MODEL || "llama-3.1-8b-instant";

export async function POST(req) {
  try {
    const body = await req.json();
    const message = body.message || "";
    const history = body.history || [];

    if (!message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    const systemPrompt = `You are CEO Atlas - the top-level AI assistant for an AI Agency Portal. You understand tasks, manage departments, and help users with agency operations. Respond in a helpful, concise manner. You can speak in Hindi/Hinglish when appropriate.`;

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

    return NextResponse.json({ response: reply, sender: "CEO Atlas" });
  } catch (error) {
    console.error("CEO Chat Error:", error);
    return NextResponse.json(
      { error: error.message || "Internal server error", response: "Error: Could not connect to AI service.", sender: "System" },
      { status: 500 }
    );
  }
}