import asyncio
import logging
from dotenv import load_dotenv
import json
import os
from time import perf_counter
from typing import Annotated
from livekit import rtc, api
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import requests

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Set up logging
logger = logging.getLogger("outbound-caller")
logger.setLevel(logging.INFO)

# System instructions for the AI agent
_default_instructions = (
    "You are an AI sales agent representing Ai Phi Auto Insurance. "
    "Your task is to call potential customers and discuss insurance options over the phone. "
    "Ensure the conversation feels natural and follows a phone call structure. "
    "1. Start with a friendly greeting: 'Hello! This is [Your Name] from Ai Phi Auto Insurance. Am I speaking with [Customer's Name]?' "
    "2. Ask politely if they have a moment to talk. If they are busy, offer to call back later. "
    "3. If they are available, introduce the purpose of the call: 'We are offering special auto insurance plans with great benefits. Have you considered getting auto insurance recently?' "
    "4. Keep sentences short and concise. Use natural pauses in the conversation. "
    "5. If they express interest, ask for their basic details: 'Great! May I have your name and age for the quote?' "
    "6. Inform them that they will receive a WhatsApp message on this number with further details and a link to our policy underwriting assistant. "
    "7. If they decline, remain polite and thank them for their time: 'No worries, thank you for your time! Have a great day.' "
    "8. Always maintain a professional but friendly tone."
)

outbound_number=os.getenv("OUTBOUND_NO") #This is the no. to be called 
twilio_number = os.getenv("TWILIO_NUMBER")

async def create_sip_participant(phone_number, room_name):
    LIVEKIT_URL = os.getenv('LIVEKIT_URL')
    LIVEKIT_API_KEY = os.getenv('LIVEKIT_API_KEY')
    LIVEKIT_API_SECRET = os.getenv('LIVEKIT_API_SECRET')
    SIP_TRUNK_ID = "ST_GqwYftU8ApJN"

    livekit_api = api.LiveKitAPI(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)

    try:
        logger.info(f"Initiating call to {phone_number} in room {room_name}")
        await livekit_api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                sip_trunk_id=SIP_TRUNK_ID,
                sip_call_to=phone_number,
                room_name=room_name,
                participant_identity=f"sip_{phone_number}",
                participant_name="Insurance Agent"
            )
        )
        await livekit_api.aclose()
        return f"Call initiated to {phone_number}"
    except Exception as e:
        logger.error(f"Error initiating call: {e}")
        await livekit_api.aclose()
        return f"Error: {str(e)}"

async def entrypoint(ctx: JobContext):
    phone_number = outbound_number  # Placeholder number
    room_name = ctx.room.name
    logger.info(f"Connecting to room {room_name}")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    result = await create_sip_participant(phone_number, room_name)
    logger.info(result)

    participant = await ctx.wait_for_participant(identity=f"sip_{phone_number}")
    run_voice_pipeline_agent(ctx, participant, _default_instructions)

    start_time = perf_counter()
    while perf_counter() - start_time < 30:
        call_status = participant.attributes.get("sip.callStatus")
        if call_status == "active":
            logger.info("User picked up")
            return
        elif participant.disconnect_reason in (
            rtc.DisconnectReason.USER_REJECTED,
            rtc.DisconnectReason.USER_UNAVAILABLE,
        ):
            logger.info("User did not pick up or rejected the call, exiting job")
            break
        await asyncio.sleep(0.1)

    logger.info("Session timed out, exiting job")
    await ctx.shutdown()

def run_voice_pipeline_agent(ctx: JobContext, participant: rtc.RemoteParticipant, instructions: str):
    logger.info("Starting voice pipeline agent")

    initial_ctx = llm.ChatContext().append(role="system", text=instructions)

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2-phonecall"),
        llm=openai.LLM(model="gpt-4o"),
        tts=deepgram.tts.TTS(model="aura-asteria-en"),
        chat_ctx=initial_ctx,
        fnc_ctx=CallActions(api=ctx.api, participant=participant, room=ctx.room, index=index),
    )
    agent.start(ctx.room, participant)




# Use Hugging Face embeddings
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Set LlamaIndex configurations
Settings.embed_model = embed_model
Settings.llm = None
Settings.chunk_size = 256
Settings.chunk_overlap = 15

# Initialize RAG for sales knowledge
PERSIST_DIR = "./insurance-knowledge-storage"

if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("insurance_data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)



class CallActions(llm.FunctionContext):
    """
    Handle call actions, including sending WhatsApp messages and SMS messages after confirmation.
    """
    def __init__(self, *, api: api.LiveKitAPI, participant: rtc.RemoteParticipant, room: rtc.Room ,index=index):
        super().__init__()
        self.api = api
        self.participant = participant
        self.room = room
        self.index = index
        
        # Twilio credentials - you'll need to load these from environment variables or config
        self.twilio_account_sid = os.getenv("twilio_account_sid")
        self.twilio_auth_token = os.getenv("twilio_auth_token")
        self.twilio_phone_number = twilio_number # Your Twilio phone number

    @llm.ai_callable()
    async def query_sales_info(
        self,
        query: Annotated[
            str,
            "The specific, focused query about product details, policy information, or technical details that requires lookup in our knowledge base. Must be a precise question seeking factual information."
        ],
    ):
        """ONLY call this function when you need specific product information, policy details, or pricing structures that are NOT common knowledge."""
        logger.info(f"Fetching sales knowledge base information for query: {query}")
        query_engine = self.index.as_query_engine(use_async=True)
        res = await query_engine.aquery(query)
        return str(res)


    @llm.ai_callable()
    async def end_call(self):
        """Called when the user wants to end the call."""
        logger.info(f"Ending the call for {self.participant.identity}")
        try:
            await self.api.room.remove_participant(
                api.RoomParticipantIdentity(
                    room=self.room.name,
                    identity=self.participant.identity,
                )
            )
        except Exception as e:
            logger.info(f"Error while ending call: {e}")

    @llm.ai_callable()
    #actual whatsapp functionalties are yet to be implimented 
    #this is a dummy function to test whats function calling
    async def send_whatsapp_confirmation(self, name: str, age: int):    
        """Sends a WhatsApp message to the user after confirming insurance interest."""
        logger.info(f"Sending WhatsApp confirmation to {self.participant.identity}")
        message = json.dumps({
            "phone": self.participant.identity,
            "message": f"Hello {name}, thank you for your interest in Ai Phi Auto Insurance! "
                       f"Since you are {age}, we have customized insurance options for you. "
                       "Check your WhatsApp for more details and our policy underwriting assistant link."
        })
        # Simulate API request
        await asyncio.sleep(2)
        return "WhatsApp confirmation sent successfully."
    
    @llm.ai_callable()
    async def send_sms_confirmation(self, name: str, age: int):
        """Sends an SMS message to the user after confirming insurance interest."""
        logger.info(f"Sending SMS confirmation to {self.participant.identity}")
        try:
            from twilio.rest import Client
            
            # Initialize Twilio client
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            # Prepare message text
            message_text = (f"Hello {name}, thank you for your interest in Ai Phi Auto Insurance! "
                          f"Since you are {age}, we have customized insurance options for you. "
                          "Our policy underwriting assistant will contact you shortly.")
            
            # Send SMS
            message = client.messages.create(
                from_=self.twilio_phone_number,
                body=message_text,
                to=outbound_number  # directly passing the phone no , have to make these credentials acessible globally
            )
            
            logger.info(f"SMS sent successfully! Message SID: {message.sid}")
            return f"SMS confirmation sent to {self.participant.identity}"
        except Exception as e:
            error_message = f"Failed to send SMS: {str(e)}"
            logger.error(error_message)
            return error_message

# def prewarm(proc: JobProcess):
#     proc.userdata["vad"] = silero.VAD.load()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="outbound-caller",
            # prewarm_fnc=prewarm,
        )
    )
