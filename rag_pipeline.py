import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

load_dotenv()

print("🔐 HuggingFace Token Loaded:", bool(os.getenv("HUGGINGFACEHUB_API_TOKEN")))
print("HUGGINGFACEHUB_API_TOKEN")
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = FAISS.load_local(
    "faiss_index_local", embedding, allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever()



llm = HuggingFaceEndpoint(
    #repo_id="tiiuae/falcon-7b-instruct",
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",  # ✅ You must explicitly specify this!
    temperature=0.1,
    max_new_tokens=200,
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)


qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

while True:
    query = input("\nYou: ")
    if query.lower() in ['exit', 'quit']:
        break
    answer = qa.run(query)
    print(f"\nBot: {answer}")
