import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Settings
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o"
TEMPERATURE = 0.2
MAX_TOKENS = 2048
STREAMING = True  # Enable streaming


# Retriever Settings
RETRIEVER_TYPE = "mmr"
TOP_K = 5
FETCH_K = 10
LAMBDA_MULT = 0.7

# ISSS Contact Information
ISSS_EMAIL = "isss@umbc.edu"
ISSS_PHONE = "410-455-2624"
ISSS_OFFICE = "University Center, Room 234"