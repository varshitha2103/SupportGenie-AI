import os
import json
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings  # ✅ Local embedding model

# Load environment variables if needed
load_dotenv()

# ✅ Use free local model instead of OpenAI
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ✅ Load your synthetic knowledge base
with open("knowledge_base/policies.json", "r", encoding="utf-8") as f:
    policy_data = json.load(f)

docs = [Document(page_content=p["content"], metadata={"title": p["title"]}) for p in policy_data]

# ✅ Split text into chunks
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# ✅ Embed and store in FAISS
vectorstore = FAISS.from_documents(chunks, embedding)
vectorstore.save_local("faiss_index_local")  # You can rename this index folder if needed

print(f"✅ Vector store created with {len(chunks)} chunks.")
