# app.py
import os
import chainlit as cl
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from openai import AsyncOpenAI
from dotenv import load_dotenv
import re
import json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from tools import create_ticket_tool, get_ticket_status_tool
import re
from ticket_store import get_ticket_status  # 👈 Import RAW version, not the @tool decorated one
from mongo_store import get_user_by_username
from mongo_store import get_all_users, get_all_tickets





# Load environment variables
load_dotenv()

# Simple in-memory user storage for demo
USERS = {
    "student1": {
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "email": "student1@umbc.edu",
        "student_id": "AB12345",
        "visa_status": "F-1",
        "program": "Computer Science"
    },
    "student2": {
        "password": "password123",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "student2@umbc.edu",
        "student_id": "CD67890",
        "visa_status": "J-1",
        "program": "Information Systems"
    }
}

# Custom prompt template with ISSS-specific instructions
PROMPT_TEMPLATE = """
        You are an AI assistant for the UMBC International Student and Scholar Services (ISSS) department.
        Answer the question based ONLY on the following context. 

        If the context contains information relevant to the query, provide a detailed, step-by-step answer.
        If you don't know the answer or cannot find it in the context, say "I don't have enough information to answer that question." 
        and suggest the student contact the ISSS office directly.

        Common topics you should be knowledgeable about include:
        - F-1/J-1 student visa processes and maintenance
        - CPT (Curricular Practical Training) application and eligibility
        - OPT (Optional Practical Training) application, timing, and requirements
        - I-20 extension and updates
        - Travel guidelines for international students
        - Employment authorization
        - SEVIS requirements
        - Academic requirements for maintaining visa status

        Make the response formatting elegant with markdown formatting.

        Context:
        {context}

        Question: {question}

        Answer:
        """
FOLLOW_UP_PROMPT ="""
        You are a helpful assistant. Based on the following user question and your answer, generate 3 concise, relevant follow-up questions the user might naturally ask next.
        Each question should be brief (under 15 words) and directly related to the previous conversation.
        Do not generate any follow up questions for general greeting messages and return empty array in this case.

        Respond ONLY with a JSON array of objects, each having "label" and "value" fields. Example format:

        sample json: {sample_action_json}

        User Question: {question}

        Your Answer:{answer}
        """


def get_user_info(username: str, password: str):
    return {
        "password":"password",
        "username":"tp34657",
        "first_name": "Manogna",
        "last_name": "Rayasam",
        "email": "tp34657@umbc.edu",
        "student_id": "tp34657",
        "visa_status": "F-1",
        "program": "Data Science"
    }


def initialize_qa_system():
    """Initialize the QA system"""
    # Initialize OpenAI embeddings
    embedding = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Load the FAISS index with OpenAI embeddings
    vectorstore = FAISS.load_local(
        "faiss_index_openai", embedding, allow_dangerous_deserialization=True
    )
    
    # Configure retriever
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 10,
            "lambda_mult": 0.7
        },
        return_source_documents=True
    )
    
    # Initialize OpenAI model
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        max_tokens=2048,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create prompt from template
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )
    
    # Create QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    
    # Store the chain in user session
    cl.user_session.set("qa_chain", qa_chain)
def initialize_agent(student_id):
    """Initialize Agno agent with ONLY ticket creation and retrieval."""
    agent = Agent(
        model=OpenAIChat(id="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
        tools=[create_ticket_tool, get_ticket_status_tool],
        instructions=[
            "You are an ISSS Chatbot agent responsible ONLY for ticket operations.",
            "If you cannot handle via ticket tools, DO NOT answer. Let the fallback system handle it.",
            f"The student's ID is: {student_id}. Use it directly when creating or fetching tickets.",
            "- If the user wants to apply, submit, or create a new OPT, CPT, or Travel I-20 ticket, call `create_ticket_tool`.",
            "- If the user asks about the status of an EXISTING ticket (mentions ticket ID like TICKET_123abc), call `get_ticket_status_tool`.",
            "- For ANY other general informational questions (e.g., 'What is OPT?', 'What is CPT?'), you should NOT answer. Leave it to the fallback system.",
            "Do NOT attempt to answer questions unrelated to tickets.",
            "Always prioritize calling the appropriate tool when ticket creation or retrieval is needed.",
            "Be direct and concise when confirming ticket actions."
        ],
        markdown=True,
        debug_mode=True,
    )
    return agent



async def generate_follow_up_questions(client, question, answer):
    """Use LLM to generate dynamic follow-up questions."""
    import json

    print(f"[FOLLOW-UP] Received question: {question}")
    print(f"[FOLLOW-UP] Received answer: {answer}")
    sample_action_json=""" [
        {"label": "How long does processing take?", "value": "How long does processing take?"},
        {"label": "What documents are needed?", "value": "What documents are needed?"},
        {"label": "Who can help if I have issues?", "value": "Who can help if I have issues?"}
        ]"""


    prompt = FOLLOW_UP_PROMPT.format(sample_action_json=sample_action_json, question=question, answer=answer)
    print(f"[FOLLOW-UP] Generated prompt for LLM:\n{prompt}")

    try:
        print(f"[FOLLOW-UP] Sending prompt to LLM...")
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        print(f"[FOLLOW-UP] Received response from LLM.")

        content = response.choices[0].message.content.strip()
        print(f"[FOLLOW-UP] Raw LLM content:\n{content}")

        # Clean up ```json ... ``` block if it exists
        content = re.sub(r"```json|```", "", content).strip()
        print(f"[FOLLOW-UP] Cleaned LLM content for JSON parsing:\n{content}")


        follow_ups = json.loads(content)

        # Safety Check: validate each follow-up
        valid_follow_ups = []
        if isinstance(follow_ups, list):
            for item in follow_ups:
                if isinstance(item, dict) and "label" in item and "value" in item:
                    valid_follow_ups.append(item)
                else:
                    print(f"[FOLLOW-UP][WARNING] Skipping invalid follow-up item: {item}")
        else:
            print(f"[FOLLOW-UP][ERROR] LLM did not return a list, got: {type(follow_ups)}")
            return []

        print(f"[FOLLOW-UP] Successfully parsed and validated follow-up questions: {valid_follow_ups}")
        return valid_follow_ups

    except json.JSONDecodeError as e:
        print(f"[FOLLOW-UP][ERROR] Failed to parse JSON from LLM response: {e}")
        return []
    except Exception as e:
        print(f"[FOLLOW-UP][ERROR] Unexpected error occurred: {e}")
        return []


async def check_if_ticket_related(client, query):
    """Ask LLM if this query is ticket-related or not"""
    prompt = f"""
    You are an assistant that helps classify whether a user's question is related to ticket operations (OPT, CPT, Travel I-20 ticket creation/status check).

    Based on the question below, answer **only** with 'Yes' or 'No':
    
    - If the user asks about creating a ticket, checking status, or mentions ticket ID, answer 'Yes'.
    - If it's about general information (e.g., What is OPT? How long is OPT? Visa travel rules?), answer 'No'.

    Question: "{query}"

    Respond ONLY with "Yes" or "No".
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        classification = response.choices[0].message.content.strip().lower()
        return classification.startswith("yes")
    except Exception as e:
        print(f"[PRECHECK][ERROR] {e}")
        return False



@cl.password_auth_callback
def auth_callback(username: str, password: str):
    print(f"[AUTH] Login attempt: {username}")

    try:
        user_info = get_user_by_username(username)
        if not user_info:
            print(f"[AUTH] User '{username}' not found!")
            return None

        if user_info.get("password") != password:
            print(f"[AUTH] Incorrect password for user '{username}'!")
            return None

        print(f"[AUTH] Successful authentication for user '{username}'")
        user_info["_id"] = str(user_info["_id"])
        return cl.User(
            identifier="admin",
            metadata={
                "role": "admin",
                "provider": "credentials",
                "user_info": user_info
            }
        )

    except Exception as e:
        print(f"[AUTH ERROR] Unexpected error during authentication: {e}")
        return None

# @cl.command(name="View Admin Dashboard", description="Display all users and tickets")
# async def admin_dashboard():
#     users = get_all_users()
#     tickets = get_all_tickets()

#     # === Build Users Table ===
#     if users:
#         user_table = "| Username | First Name | Last Name | Email |\n"
#         user_table += "|---|---|---|---|\n"
#         for user in users:
#             user_table += f"| {user.get('username', '')} | {user.get('first_name', '')} | {user.get('last_name', '')} | {user.get('email', '')} |\n"
#     else:
#         user_table = "No users found."

#     # === Build Tickets Table ===
#     if tickets:
#         ticket_table = "| Ticket ID | Student ID | Type | Status | Created At |\n"
#         ticket_table += "|---|---|---|---|---|\n"
#         for ticket in tickets:
#             ticket_table += f"| {ticket.get('ticket_id', '')} | {ticket.get('student_id', '')} | {ticket.get('ticket_type', '')} | {ticket.get('status', '')} | {ticket.get('created_at', '')} |\n"
#     else:
#         ticket_table = "No tickets found."

#     # === Send the message ===
#     await cl.Message(
#         content=f"# 📋 Admin Dashboard\n\n"
#                 f"## 👥 Users\n\n{user_table}\n\n"
#                 f"## 🎫 Tickets\n\n{ticket_table}"
#     ).send()

# Create the welcome screen and topic options
@cl.on_chat_start
async def show_welcome_screen():
    """Show the welcome screen with personalized content"""
    initialize_qa_system()
 
    if cl.user_session.get("user_info") is None:
        user = cl.user_session.get("user")  # ✅ Correct way
        if user:
            user_info = user.metadata.get("user_info")
            if user_info:
                cl.user_session.set("user_info", user_info)

    user_info = cl.user_session.get("user_info")
    if not user_info:
        await cl.Message(content="Session expired. Please refresh the page.").send()
        return
    
    # Personalized welcome message
    await cl.Message(
        content=f"# 👋 Welcome to the UMBC ISSS Chatbot, {user_info['first_name']}!\n\nI can help answer your questions about international student services at UMBC. Choose a topic below to get started or type your own question."
    ).send()
    
    # Popular topics as clickable buttons
    actions = [
        cl.Action(
            name="opt_action",
            payload={"value": "Tell me about Optional Practical Training (OPT)"},
            label="OPT Information"
        ),
        cl.Action(
            name="cpt_action",
            payload={"value": "How do I apply for Curricular Practical Training (CPT)?"},
            label="CPT Application"
        ),
        cl.Action(
            name="i20_action",
            payload={"value": "I need to extend my I-20. What are the steps?"},
            label="I-20 Extension"
        ),
        cl.Action(
            name="visa_action",
            payload={"value": "What should I do if my F-1 visa is expiring?"},
            label="F-1 Visa Issues"
        ),
        cl.Action(
            name="travel_action",
            payload={"value": "Can I travel outside the US while on OPT?"},
            label="Travel Guidelines"
        )
    ]
    
    await cl.Message(
        content="## Popular Topics",
        actions=actions
    ).send()

# Handle topic selection from the welcome screen
@cl.action_callback("opt_action")
@cl.action_callback("cpt_action")
@cl.action_callback("i20_action")
@cl.action_callback("visa_action")
@cl.action_callback("travel_action")
async def on_topic_action(action):
    # Get user info
    user_info = cl.user_session.get("user_info")
    if not user_info:
        # This shouldn't happen, but just in case
        await cl.Message(content="Session expired. Please refresh the page.").send()
        return
    
    # Get the value from the payload
    question = action.payload.get("value")
    
    # Create a new user message with the question
    await cl.Message(author=user_info.get("first_name", "User"), content=question).send()
    
    # Process the message with personalization
    await process_message_with_personalization(question, user_info)

@cl.on_message
async def on_message(message: cl.Message):
    # Get user info
    user_info = cl.user_session.get("user_info")
    if not user_info:
        # If no user info, ask to refresh
        await cl.Message(content="Session expired. Please refresh the page.").send()
        return
    
    # Process the message with personalization
    await process_message_with_personalization(message.content, user_info)

async def process_message_with_personalization(query, user_info):
    student_id = user_info.get("student_id")
    
    # Step 0: Pre-check if this is ticket-related
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    ticket_related = await check_if_ticket_related(client, query)

    if ticket_related:
        # Step 1: Ticket related - Call agent
        agent = initialize_agent(student_id)
        try:
            response = agent.run(query, tool_kwargs={"student_id": student_id})
            if response:
                if hasattr(response, "content") and response.content:
                    await cl.Message(content=response.content).send()
                elif hasattr(response, "message") and response.message:
                    await cl.Message(content=response.message).send()
            return  # Always stop after agent response
        except Exception as e:
            print(f"[AGNO][ERROR] {e}")
            await cl.Message(content="There was an error processing your ticket request.").send()
            return

    # Step 2: Non-ticket, fallback to FAISS QA
    qa_chain = cl.user_session.get("qa_chain")
    retriever = qa_chain.retriever
    context_docs = retriever.get_relevant_documents(query)
    await process_streaming_response(query, context_docs, user_info)




    # Step 2b: If agent didn't act (normal question), fallback to LangChain QA
    # qa_chain = cl.user_session.get("qa_chain")
    # retriever = qa_chain.retriever
    # context_docs = retriever.get_relevant_documents(query)
    # await process_streaming_response(query, context_docs, user_info)




async def process_streaming_response(query, context_docs, user_info):
    """Generate streaming response with personalization"""
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Prepare context from documents
    context_text = ""
    if context_docs and len(context_docs) > 0:
        context_text = "Context information:\n"
        for i, doc in enumerate(context_docs):
            context_text += f"Document {i+1}:\n{doc.page_content}\n\n"
    
    # Add user personalization
    personalization = ""
    if user_info and user_info.get("first_name") != "Guest":
        personalization = f"""
        User information:
        - Name: {user_info.get('first_name', '')} {user_info.get('last_name', '')}
        - Email: {user_info.get('email', '')}
        - Student ID: {user_info.get('student_id', '')}
        - Visa Status: {user_info.get('visa_status', '')}
        - Program: {user_info.get('program', '')}
        """
            
    # Create system message
    system_message = {
        "role": "system",
        "content": f"""You are an AI assistant for the UMBC International Student and Scholar Services (ISSS) department.
            Answer the question based ONLY on the provided context. If you don't know the answer or cannot find it in the context,
            say "I don't have enough information to answer that question" and suggest contacting the ISSS office directly.

            {personalization}

            When appropriate, personalize your responses to the user by referring to them by name and considering their specific
            situation (visa status, program of study, etc.). If they are a guest user, provide general information.

            Do not include citation brackets in your response."""
                }
    
    # Create user message
    user_message = {
        "role": "user",
        "content": f"{context_text}\n\nQuestion: {query}"
    }
    
    # Start streaming response
    msg = cl.Message(content="")
    await msg.send()
    collected_answer = ""

    
    try:
        # Create streaming completion
        stream = await client.chat.completions.create(
            model="gpt-4o",
            messages=[system_message, user_message],
            temperature=0.2,
            max_tokens=2048,
            stream=True
        )
        print("Before streaming response")
        # Process streaming response
        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await msg.stream_token(token)
                collected_answer += token
        
        print("After streaming response")
         # After streaming, call LLM to generate follow-ups
        follow_ups = await generate_follow_up_questions(client, query, collected_answer)
        print("Follow ups received")
        print(follow_ups)
        if follow_ups:
            print("Follow ups exist")
            actions = [
                cl.Action(
                    name=f"followup_{i+1}",
                    payload={"value": followup["value"]},
                    label=followup["label"]
                )
                for i, followup in enumerate(follow_ups)
            ]
            print("follow_ups done")
            print(follow_ups)
            await cl.Message(content="Would you like to explore any of these follow-up questions?", actions=actions).send()
        else:
            await cl.Message(content="Let me know if you have any follow-up questions!").send()
        
    except Exception as e:
        error_message = f"I encountered an error while processing your request: {str(e)}"
        await cl.Message(content=error_message).send()
        print(f"Error: {str(e)}")

# Handle follow-up questions
@cl.action_callback("followup_1")
@cl.action_callback("followup_2")
@cl.action_callback("followup_3")
async def on_followup(action):
    # Get user info
    user_info = cl.user_session.get("user_info")
    if not user_info:
        await cl.Message(content="Session expired. Please refresh the page.").send()
        return
    
    # Get the value from the payload
    question = action.payload.get("value")
    
    # Create a new user message with the question
    await cl.Message(author=user_info.get("first_name", "User"), content=question).send()
    
    # Process the message with personalization
    await process_message_with_personalization(question, user_info)