# AI Voice Caller Agent

## Overview

The AI Voice Caller Agent is an automated outbound calling system designed to engage potential customers in conversations about auto insurance. It leverages AI-driven voice interactions using LiveKit, OpenAI, and Deepgram for real-time speech processing, natural language understanding, and text-to-speech synthesis.

## Features

- **AI-driven conversational agent**: Utilizes OpenAI's GPT-4o for natural conversation handling.
- **Real-time speech processing**: Employs Deepgram for speech-to-text and text-to-speech capabilities.
- **LiveKit integration**: Facilitates real-time voice communication.
- **Hugging Face embeddings**: Enhances response accuracy with a sales knowledge base.
- **Automated WhatsApp and SMS notifications**: Confirms user interest and provides follow-up information.
- **Twilio SIP support**: Places outbound calls to customers via SIP integration.

## Technology Stack

- **Python**
- **LiveKit API**
- **OpenAI GPT-4o**
- **Deepgram Speech Processing**
- **Hugging Face Embeddings**
- **Twilio API**
- **LlamaIndex for RAG-based Knowledge Retrieval**

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.8+
- `pip` (Python package manager)
- Virtual environment (optional but recommended)
- LiveKit CLI (`lk`) installed. Follow [LiveKit CLI Installation Guide](https://docs.livekit.io/reference/livekit-cli/)

### Setup

1. **Clone the repository**:
   ```sh
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Obtain API Keys and Credentials**:

   - **LiveKit API Keys**:
     - Sign in to the [LiveKit Cloud Dashboard](https://cloud.livekit.io/).
     - Navigate to your project or create a new one.
     - Access the API keys section to retrieve your `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET`.
     - For detailed instructions, refer to the [LiveKit Authentication Guide](https://docs.livekit.io/home/get-started/authentication/).

   - **Twilio Credentials**:
     - Log in to the [Twilio Console](https://www.twilio.com/console).
     - Navigate to the dashboard to find your `twilio_account_sid` and `twilio_auth_token`.
     - For more information, see Twilio's [Access Tokens Documentation](https://www.twilio.com/docs/iam/access-tokens).

   - **SIP Trunk ID**:
     - To set up a SIP trunk and obtain the `SIP_TRUNK_ID`, follow the [LiveKit SIP Trunk Configuration Guide](https://docs.livekit.io/sip/quickstarts/configuring-sip-trunk/).
     - For Twilio-specific SIP trunk setup, refer to [LiveKit's Twilio SIP Trunk Configuration](https://docs.livekit.io/sip/quickstarts/configuring-twilio-trunk/).

5. **Configure Environment Variables**:

   Create a `.env.local` file in the project directory with the following content:

   ```ini
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

   Replace the placeholders with the actual values obtained in the previous steps.

## Usage

To start the AI Voice Caller Agent:

1. **Run the application**:
   ```sh
   python ai_voice_caller.py dev
   ```
   This command initiates the AI voice caller agent in development mode.

2. **Dispatch an Outbound Call**:
   - Open a new terminal.
   - Use the following command to dispatch a call:
     ```sh
     lk --api-key=<LIVEKIT_API_KEY> --api-secret=<LIVEKIT_API_SECRET> --url=<LIVEKIT_URL> dispatch create --new-room --agent-name outbound-caller --metadata '<no_to_be_called>'
     ```
     This command creates a new room and initiates an outbound call to the specified phone number.

3. **Monitor the logs**:
   - Open another terminal window.
   - Navigate to the project directory.
   - Execute the following command to tail the logs:
     ```sh
     tail -f logs/ai_voice_caller.log
     ```
     This allows you to monitor real-time logs and observe the agent's behavior during calls.

## How It Works

1. **Outbound Call Initiation**: The agent places an outbound call to the specified phone number using Twilio SIP.
2. **AI-Driven Conversation**: Upon answering, the AI agent engages the user in a structured conversation about auto insurance options.
3. **Real-Time Speech Processing**: The system utilizes Deepgram for speech-to-text and text-to-speech conversion, ensuring natural and responsive communication.
4. **Interest Confirmation**: If the customer expresses interest, the agent sends a WhatsApp or SMS confirmation using Twilio's messaging services.
5. **Knowledge Retrieval**: The AI retrieves relevant sales information from the knowledge base using LlamaIndex for accurate and informed responses.

## Customization

- **Conversation Flow**: Modify the `_default_instructions` variable in `ai_voice_caller.py` to change the conversational script and flow.
- **Additional Actions**: Extend the `CallActions` class to implement additional functionalities such as email follow-ups or scheduling callbacks.
- **Knowledge Base**: Update the `insurance_data` directory with relevant documents to enhance the AI's knowledge base and response accuracy.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

*Note: Ensure all API keys and credentials are kept secure and not exposed in public repositories or shared environments.*

