# 🎯 Real-Time Voice AI Agents Suite  
Empowering Human-Like Voice Intelligence for Automation — in Real Time

Welcome to the Real-Time Voice AI Agents Suite — a powerful, full-stack voice-first platform designed for seamless real-time interaction, business logic execution, and intelligent decision-making. This system integrates voice, function-calling, retrieval-augmented generation (RAG), and domain-specific agents — all through an ultra-low latency experience.

---

## ⚡ Real-Time First. Always.

This system is architected for real-time responsiveness — every interaction, whether via browser or phone call, is processed and responded to instantly. Real-time streaming, retrieval, and execution ensure a fluid and natural conversational experience.

- 🔄 Bi-directional voice streaming over WebRTC
- 🧠 Instant agent thinking powered by live RAG pipelines
- ⚙️ Live backend function execution during conversations
- 📞 Real-world phone calls via Twilio Voice integration

---

## 🌟 Key Features

### 🎙 Real-Time Voice Interface (WebRTC)
- Low-latency voice input and output
- Built for natural, flowing conversations
- Supports browser-based mic input and playback

### 📞 Phone Calling with Twilio
- Make and receive real phone calls with the AI agent
- Twilio integration bridges PSTN to your AI stack
- Enables real-time voice automation for customer service, sales, and support

### 🧠 Unified All-in-One Agent
- Handles voice, knowledge, tools, and action in one place
- Multimodal RAG: Retrieves data from APIs, documents, search, and more
- Executes backend logic (function-calling) live in response to user prompts

### 📊 Domain-Specific Insurance Underwriting Agent
- Trained for policy Q&A, risk evaluation, and decision making
- Parses customer queries, assesses documents, and provides actionable insights
- Built to reduce manual overhead in the underwriting pipeline

---

## 🛠️ Tech Stack Overview

| Layer        | Technology                                                   |
|--------------|--------------------------------------------------------------|
| Frontend     | React / Streamlit + WebRTC voice streaming                   |
| Backend      | FastAPI + LangChain / CrewAI + WebSockets                    |
| Voice I/O    | Real-time streaming + TTS via Hugging Face                   |
| LLMs         | GROQ, Mistral, or open-source LLMs                           |
| RAG Layer    | FAISS / Chroma + Cohere / OpenAI embeddings                  |
| Telephony    | Twilio Programmable Voice (Phone calling capabilities)       |

---

## 🧩 Modular Architecture

📂 Project Structure:

.
├── frontend/              → 🎛️ Real-time voice UI (WebRTC-enabled)  
├── backend/               → 🧠 AI logic, agents, tools, RAG pipeline  
├── insurance-agent/       → 📑 Insurance underwriting logic and context  

Each directory includes its own setup and configuration guide.

---

## ⚙️ How It Works

1. 🎤 Speak via browser or phone — voice is streamed in real time
2. 🔎 System retrieves context using multimodal RAG
3. ⚙️ Live functions are called for decision-making or data
4. 🗣 AI replies instantly via TTS and streams the response back

Whether you're interacting via a browser or dialing in via phone, the experience is fully real-time, natural, and context-aware.

---

## 🚀 Quickstart

Clone the repository:

```bash
git clone https://github.com/your-org/realtime-voice-agents.git
cd realtime-voice-agents

