# 🤖 SupportGenieAI – RAG-Powered ISSS Chatbot

**SupportGenieAI** is a smart, privacy-preserving chatbot designed to simulate international student support at UMBC. Built using **Retrieval Augmented Generation (RAG)**, the system pulls up-to-date information from university websites and responds to user queries in a human-like, multi-turn conversation format.

---

## 🚀 Features

- 🔄 Retrieval-Augmented Generation (RAG) pipeline using LangChain
- 🧠 HuggingFace BGE embeddings stored in FAISS via ChromaDB
- 💬 Multi-turn conversation support using conversational retrieval chains
- 🕷 Web scraping via BeautifulSoup, ScrapeGraph, and Crawl4AI
- 🌐 Streamlit-based UI for real-time interaction
- 🔒 Synthetic knowledge base with no use of real student data

---

## 🛠 Tech Stack

| Component         | Tooling Used                                 |
|------------------|-----------------------------------------------|
| LLM              | OpenAI GPT-3.5 / GPT-4                        |
| Embedding Model  | HuggingFace BGE v1.5                          |
| Vector Store     | FAISS (via ChromaDB)                          |
| Web Scraping     | BeautifulSoup · ScrapeGraph · Crawl4AI        |
| UI Framework     | Streamlit                                     |
| Pipeline Logic   | LangChain + LangGraph                         |

---

## 📖 Medium Blog Post

Read the full development story, architecture explanation, and demo:

👉 [Building SupportGenieAI – A Smart ISSS Chatbot Using LangChain + Streamlit]([https://medium.com/your-blog-link-here](https://medium.com/@varshi.yanamala/supportgenie-building-a-smart-isss-chatbot-with-rag-langchain-and-streamlit-e4f0166c1c1c))

---

## 💡 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/varshitha2103/SupportGenieAI.git
cd SupportGenieAI
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up your environment
Create a .env file and add your API keys:
OPENAI_API_KEY=your_openai_key

4. Run the Streamlit app
streamlit run streamlit_app.py

🧠 What We Learned
Building production-ready RAG pipelines with LangChain
Designing privacy-aware AI applications using synthetic datasets
Managing web scraping + vector storage sync pipelines
UI deployment with Streamlit for real-time chatbot interaction'
