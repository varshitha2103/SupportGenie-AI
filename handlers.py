# handlers.py
import re
import chainlit as cl
import config

async def process_message(user_query):
    """Process a user message and generate a response with streaming"""
    
    # Get the chain from user session
    qa_chain = cl.user_session.get("qa_chain")
    
    # Create a custom callback handler for streaming
    callback = cl.LangchainCallbackHandler()
    
    # Show a thinking message first
    thinking_msg = await cl.Message(content="Thinking...").send()
    
    try:
        # Create a new message for the response instead of updating
        msg = cl.Message(content="")
        await msg.send()
        
        # Process the query
        response = qa_chain.invoke(
            {"query": user_query},
            callbacks=[callback]
        )
        
        answer = response["result"]
        source_documents = response.get("source_documents", [])
        
        # Handle case with no relevant documents
        if not source_documents:
            await cl.Message(
                content=f"I don't have enough information to answer that question. Please contact the ISSS office directly at {config.ISSS_EMAIL} or call {config.ISSS_PHONE} for assistance."
            ).send()
            return
        
        # Replace bracketed citation numbers with empty string to remove them
        clean_answer = re.sub(r'\[(\d+)\]', '', answer)
        
        # Send a new message with the answer instead of updating
        await cl.Message(content=clean_answer).send()
        
        # Follow-up questions as action buttons
        actions = [
            cl.Action(
                name="followup_1",
                payload={"value": "What documents do I need for this process?"},
                label="What documents do I need?"
            ),
            cl.Action(
                name="followup_2",
                payload={"value": "What are the deadlines I should be aware of?"},
                label="What are the deadlines?"
            ),
            cl.Action(
                name="followup_3",
                payload={"value": "Who should I contact for more help?"},
                label="Who to contact?"
            )
        ]
        
        await cl.Message(content="Do you have any follow-up questions?", actions=actions).send()
        
    except Exception as e:
        # Handle errors gracefully - send a new message instead of updating
        error_message = f"I encountered an error while processing your request: {str(e)}"
        await cl.Message(content=error_message).send()
        # Log the error for debugging
        print(f"Error: {str(e)}")