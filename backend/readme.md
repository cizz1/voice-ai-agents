# AI Insurance Underwriting Agent

This is an AI-powered insurance underwriting voice agent designed to assist customers in obtaining auto insurance quotes. The agent, named Sadie Matthews, gathers customer details, evaluates risk, calculates premiums, and provides underwriting recommendations. It is built using LiveKit for real-time interactions and integrates RAG for policy knowledge retrieval.

## Features
- **Real-Time Voice Conversations**: Uses LiveKit for handling voice interactions.
- **Risk Assessment & Premium Calculation**: Determines insurance premium based on customer inputs.
- **RAG-Enhanced Knowledge Retrieval**: Retrieves policy details when necessary.
- **STT & TTS**: Uses Deepgram for speech-to-text and text-to-speech.
- **LLM-Powered Conversations**: Driven by OpenAI's GPT-4o.
- **Escalation to Sales Representative**: Connects high-priority customers to a human agent (functionality not yet implemented but can be achieved using Twilio integration and SIP setup; refer to `ai_voice_caller.py` for guidance).

## Cloning the Repository
To use this project, first clone the repository:

```bash
# Clone the repo
git clone <repository-url>

# Navigate into the project directory
cd <repository-folder>
```

The repository consists of two folders: `frontend` and `backend`. Use `cd` to navigate between them.

## Environment Variables
The project requires separate `.env` files for the frontend and backend.

### Backend (`.env`)
Create a `.env` file in the `backend` directory and define the following environment variables:

```env
LIVEKIT_URL=<your_livekit_url>
LIVEKIT_API_KEY=<your_livekit_api_key>
LIVEKIT_API_SECRET=<your_livekit_api_secret>
OUTBOUND_NO=<customer_phone_number>
TWILIO_NUMBER=<your_twilio_number>
twilio_account_sid=<your_twilio_account_sid>
twilio_auth_token=<your_twilio_auth_token>
SIP_TRUNK_ID=<your_sip_trunk_id>
OPENAI_API_KEY=<your_openai_api_key>
GROQ_API_KEY=<your_groq_api_key>
SIP_OUTBOUND_TRUNK_ID=<your_sip_outbound_trunk_id>
DEEPGRAM_API_KEY=<your_deepgram_api_key>
```

### Frontend (`.env.local`)
Create a `.env.local` file in the `frontend` directory with the following environment variables:

```env
LIVEKIT_API_KEY=<your_api_key>
LIVEKIT_API_SECRET=<your_api_key>
LIVEKIT_URL=wss://<project-subdomain>.livekit.cloud
```

## Running the Project
1. Clone the repository and navigate to the project directory.
2. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
3. Install dependencies for the backend:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend:
   ```bash
   python sales.py start
   ```
5. Open a new terminal and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
6. Install frontend dependencies:
   ```bash
   npm install
   ```
7. Run the frontend:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5000`.

## SIP Trunk Setup for Call Dispatch
This agent integrates with Twilio SIP trunking for live sales rep connections. Ensure your SIP trunk is properly configured in Twilio and set `SIP_TRUNK_ID` in `.env`.

## How It Works
1. **Gathers customer details**: Asks for age, driving experience, vehicle type, accident history, etc.
2. **Evaluates risk**: Calculates a risk score based on provided inputs.
3. **Determines premium**: Uses predefined risk factors and income adjustments.
4. **Provides policy recommendations**: Suggests coverage options based on customer profile.
5. **Handles escalation**: Routes high-risk or high-priority customers to a human representative via SIP trunk (not yet implemented but can be added easily).

## Customization
The `@llm_callable` functions can be modified to suit user needs, allowing adjustments to risk assessment, premium calculation, and call handling logic.

## Tech Stack
- **LiveKit** (for real-time voice interactions)
- **OpenAI GPT-4o** (for natural conversations)
- **Deepgram STT/TTS** (for speech processing)
- **LlamaIndex** (for RAG-powered knowledge retrieval)
- **Twilio SIP** (for call dispatch to human agents)

## Future Enhancements
- Support for multiple policy types (home, health, etc.)
- Multi-modal document analysis for claims processing
- Integration with CRM for lead management

