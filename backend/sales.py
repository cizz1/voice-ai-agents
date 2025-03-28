#non working code

import asyncio
import re
import os
from typing import Annotated
from dotenv import load_dotenv
from livekit import agents, rtc, api
from livekit.agents import JobContext, WorkerOptions, cli, tokenize, tts
from livekit.agents.llm import (
    ChatContext,
    ChatMessage,
    ChatImage,
    FunctionContext
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

load_dotenv(dotenv_path=".env.local")

# Use Hugging Face embeddings
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

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

class SalesUnderwritingFunction(FunctionContext):
    # @agents.llm.ai_callable(
    #     description="Called when user asks a query that can be answered using the sales knowledge base"
    # )
    # async def query_sales_info(
    #     self,
    #     query: Annotated[
    #         str,
    #         agents.llm.TypeInfo(
    #             description="The user asked query to search in the sales knowledge base"
    #         )
    #     ],
    # ):
    #     print(f"Answering from knowledgebase: {query}")
    #     query_engine = index.as_query_engine(use_async=True)
    #     res = await query_engine.aquery(query)
    #     print("Query result:", res)
    #     return str(res)


    @agents.llm.ai_callable(
        description="ONLY call this function when you need specific product information, policy details, "
        "or pricing structures that are NOT common knowledge. DO NOT use for basic conversation, "
        "gathering customer information, or responding to simple questions. This function should ONLY "
        "be used when you need to retrieve specific documented information from our knowledge base. Using this function has high computational cost and should be avoided unless absolutely necessary."
    )
    async def query_sales_info(
        self,
        query: Annotated[
            str,
            agents.llm.TypeInfo(
                description="The specific, focused query about product details, policy information, or technical details that requires lookup in our knowledge base. Must be a precise question seeking factual information."
            )
        ],
    ):
        print(f"Answering from knowledgebase: {query}")
        query_engine = index.as_query_engine(use_async=True)
        res = await query_engine.aquery(query)
        print("Query result:", res)
        return str(res)

    @agents.llm.ai_callable(
        description="Evaluates customer risk and calculates auto insurance premium in INR"
    )
    async def evaluate_customer(
        self,
        age: Annotated[
            int,
            agents.llm.TypeInfo(
                description="Customer's age"
            )
        ],
        driving_experience: Annotated[
            int,
            agents.llm.TypeInfo(
                description="Number of years of driving experience"
            )
        ],
        vehicle_type: Annotated[
            str,
            agents.llm.TypeInfo(
                description="Type of vehicle (SUV, Car, Motorbike)"
            )
        ],
        tickets_accidents: Annotated[
            int,
            agents.llm.TypeInfo(
                description="Number of traffic tickets or accidents in the past 5 years"
            )
        ],
        annual_income: Annotated[
            int,
            agents.llm.TypeInfo(
                description="Customer's annual income in INR"
            )
        ]
    ):
        # Log received inputs
        print(f"\n--- Starting Premium Calculation ---")
        print(f"Received Inputs -> Age: {age}, Driving Experience: {driving_experience} years, Vehicle Type: {vehicle_type}, Tickets/Accidents: {tickets_accidents}, Annual Income: ₹{annual_income}")

        # Base risk score
        risk_score = 50
        print(f"Initial Risk Score: {risk_score}")

        # Age factor
        if age < 25:
            risk_score += 30  
            print(f"Age < 25: +30 Risk Score (New: {risk_score})")
        elif age > 60:
            risk_score += 15  
            print(f"Age > 60: +15 Risk Score (New: {risk_score})")

        # Driving experience factor
        if driving_experience < 2:
            risk_score += 25  
            print(f"Driving Experience < 2 years: +25 Risk Score (New: {risk_score})")
        elif driving_experience < 5:
            risk_score += 15  
            print(f"Driving Experience < 5 years: +15 Risk Score (New: {risk_score})")

        # Vehicle type factor
        vehicle_risk = {
            "motorbike": 50,  
            "suv": 30,  
            "car": 10  
        }
        risk_score += vehicle_risk.get(vehicle_type.lower(), 10)
        print(f"Vehicle Type: {vehicle_type} → Risk Score Adjustment: +{vehicle_risk.get(vehicle_type.lower(), 10)} (New: {risk_score})")

        # Tickets/Accidents factor
        risk_score += tickets_accidents * 20  
        print(f"Tickets/Accidents ({tickets_accidents}): +{tickets_accidents * 20} Risk Score (New: {risk_score})")

        # Income factor
        if annual_income < 500000:
            risk_score += 20  
            print(f"Annual Income < ₹5,00,000: +20 Risk Score (New: {risk_score})")
        elif annual_income > 2000000:
            risk_score -= 10  
            print(f"Annual Income > ₹20,00,000: -10 Risk Score (New: {risk_score})")

        # Base Premium Rates
        base_premium = {
            "motorbike": 5000,  
            "car": 10000,  
            "suv": 15000  
        }
        
        # Get base premium for vehicle type
        base_price = base_premium.get(vehicle_type.lower(), 10000)
        print(f"Base Premium for {vehicle_type}: ₹{base_price}")

        # Apply No-Claim Bonus (NCB) discount
        ncb_discount = 0.1 * base_price if tickets_accidents == 0 else 0
        print(f"No-Claim Bonus Discount: -₹{ncb_discount}")

        # Adjust premium based on risk score
        risk_multiplier = 1 + (risk_score / 200)
        final_premium = (base_price * risk_multiplier) - ncb_discount

        print(f"Risk Multiplier: {risk_multiplier}")
        print(f"Final Premium (After Risk Score & NCB Adjustment): ₹{round(final_premium, 2)}")

        print(f"--- Premium Calculation Completed ---\n")

        return {
            "risk_score": risk_score,
            "tier": "Low Risk" if risk_score <= 80 else "Moderate Risk" if risk_score <= 120 else "High Risk",
            "base_premium": f"₹{base_price}",
            "final_premium": f"₹{round(final_premium, 2)}"
        }



    # @agents.llm.ai_callable(
    #     description="Called when a user wants to book a sales call"
    # )
    # async def book_sales_call(
    #     self,
    #     email: Annotated[
    #         str,
    #         agents.llm.TypeInfo(
    #             description="Email address for the sales call"
    #         )
    #     ],
    #     company_name: Annotated[
    #         str,
    #         agents.llm.TypeInfo(
    #             description="Name of the customer's company"
    #         )
    #     ],
    #     contact_name: Annotated[
    #         str,
    #         agents.llm.TypeInfo(
    #             description="Name of the contact person"
    #         )
    #     ]
    # ):
    #     if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
    #         return "The email address seems incorrect. Please provide a valid one."

    #     try:
    #         webhook_url = os.getenv('WEBHOOK_URL')
    #         headers = {'Content-Type': 'application/json'}
    #         data = {'email': email, 'company_name': company_name, 'contact_name': contact_name}
    #         response = requests.post(webhook_url, json=data, headers=headers)
    #         response.raise_for_status()
    #         return f"Sales call booking link sent to {email}. Please check your email."
    #     except requests.RequestException as e:
    #         print(f"Error booking sales call: {e}")
    #         return "There was an error booking your sales call. Please try again later."

    # @agents.llm.ai_callable(
    #     description="Called when a priority customer needs immediate assistance"
    # )
    # async def escalate_to_sales_rep(
    #     self,
    #     urgency_level: Annotated[
    #         str,
    #         agents.llm.TypeInfo(
    #             description="Urgency level: high, medium, or low"
    #         )
    #     ],
    #     issue_summary: Annotated[
    #         str,
    #         agents.llm.TypeInfo(
    #             description="Brief summary of the customer's issue"
    #         )
    #     ]
    # ):
    #     if urgency_level.lower() == "high":
    #         return "connect_sales_rep"
    #     else:
    #         return "Your request has been noted. Our sales team will prioritize your case and contact you within 24 hours."

async def get_video_track(room: rtc.Room):
    video_track = asyncio.Future[rtc.RemoteVideoTrack]()
    for _, participant in room.remote_participants.items():
        for _, track_publication in participant.track_publications.items():
            if track_publication.track is not None and isinstance(
                track_publication.track, rtc.RemoteVideoTrack
            ):
                video_track.set_result(track_publication.track)
                print(f"Using video track {track_publication.track.sid}")
                break
    return await video_track

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    print(f"Connected to room: {ctx.room.name}")

    initial_ctx = ChatContext(
        messages=[
            ChatMessage(
                role="system",
                content=(
                "You are Sadie Matthews, an Auto Insurance Underwriting Specialist at Ai PHI Solutions. "
                "Your job is to gather customer information, calculate a risk score, determine a premium, "
                "and underwrite an auto insurance policy. "

                "**CONVERSATION STYLE:** "
                "- Keep responses concise (1-2 sentences). "
                "- Ask only ONE question at a time and wait for the customer’s response. "
                "- Maintain a warm, professional, and consultative tone—think of yourself as a friendly insurance advisor. "
                "- Use natural pauses and transition phrases like: "
                "  - 'Great! Now let’s talk about your driving history…' "
                "  - 'Got it! Just a couple more details, and I’ll calculate your premium.' "

                "**INFORMATION GATHERING SEQUENCE:** "
                "1. **Vehicle Details** – Ask about the make, model, and year of the car. "
                "2. **Driver Profile** – Ask about the customer’s age and driving experience. "
                "3. **Driving History** – Ask about past accidents or tickets. "
                "4. **Current Coverage** – Ask if they have existing auto insurance. "
                "5. **Coverage Needs** – Understand their insurance priorities (e.g., full coverage vs. liability-only). "
                "6. **Annual Income** – Ask about their annual income to assess eligibility for premium adjustments. "

                "**UNDERWRITING & POLICY OFFERING:** "
                "- Use the provided data to calculate a **risk score** and **premium estimate**. "
                "- Present coverage options in a clear and easy-to-understand way. "
                "- If needed, pull **specific policy details** from the knowledge base but **only when absolutely necessary** "
                "(e.g., precise coverage limits, discount eligibility). "
                "- After providing the premium estimate, **encourage the customer to finalize the policy** with a friendly closing statement. "

                "**IMPORTANT:** Always complete the full information-gathering process **before discussing pricing or underwriting decisions**. "
                "If the customer asks about pricing too early, politely guide them back by saying: "
                "  - 'I’d love to give you an exact quote! First, let’s go over a few details about your car and driving history.' "

                "Your goal is to **provide expert guidance while making the insurance process feel simple and stress-free!**"

                ),
            )
        ]
    )

    latest_image = None
    sales_rep_connected = False

    chat = rtc.ChatManager(ctx.room)

    assistant = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        # llm=openai.LLM.with_groq(model="llama-3.3-70b-versatile"),
        llm=openai.LLM(model="gpt-4o"),
        tts=deepgram.tts.TTS(model="aura-asteria-en"),
        chat_ctx=initial_ctx,
        fnc_ctx=SalesUnderwritingFunction(),
        max_nested_fnc_calls=10,
    )

    @chat.on("message_received")
    def on_message_received(msg: rtc.ChatMessage):
        if msg.message and not sales_rep_connected:
            asyncio.create_task(assistant.say(msg.message, allow_interruptions=True))
        elif msg.message and sales_rep_connected and "help me" in msg.message.lower():
            asyncio.create_task(assistant.say(msg.message, allow_interruptions=True))

    @assistant.on("function_calls_finished")
    def on_function_calls_finished(called_functions: list[agents.llm.CalledFunction]):
        nonlocal sales_rep_connected
        if len(called_functions) == 0:
            return
        
        function = called_functions[0]
        function_name = function.call_info.function_info.name
        print(f"Called function: {function_name}")
        
        if function_name == "escalate_to_sales_rep":
            result = function.result
            if result == "connect_sales_rep":
                print("Connecting to sales representative")
                sales_rep_phone = os.getenv('SALES_REP_PHONE')
                asyncio.create_task(connect_sales_representative(sales_rep_phone, ctx.room.name))
                sales_rep_connected = True
            else:
                asyncio.create_task(
                    assistant.say(result, allow_interruptions=True)
                )

    assistant.start(ctx.room)
    await assistant.say(
    "Hi, I'm Sadie from Ai PHI Auto Insurance. What kind of vehicle are you looking to insure?",
    allow_interruptions=True
    )

    while ctx.room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
        try:
            video_track = await get_video_track(ctx.room)
            async for event in rtc.VideoStream(video_track):
                latest_image = event.frame
                await asyncio.sleep(1)
        except:
            await asyncio.sleep(1)

async def connect_sales_representative(phone_number, room_name):
    print("Attempting to connect sales representative")
    livekit_api = api.LiveKitAPI(
        os.getenv('LIVEKIT_URL'),
        os.getenv('LIVEKIT_API_KEY'),
        os.getenv('LIVEKIT_API_SECRET')
    )

    await livekit_api.sip.create_sip_participant(
        api.CreateSIPParticipantRequest(
            sip_trunk_id=os.getenv('SIP_TRUNK_ID'),
            sip_call_to=phone_number,
            room_name=room_name,
            participant_identity=f"sip_{phone_number}",
            participant_name="Sales Representative",
            play_ringtone=1
        )
    )
    await livekit_api.aclose()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))