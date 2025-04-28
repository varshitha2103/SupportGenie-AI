# rebuild_index.py with encoding error handling
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Load environment variables
load_dotenv()

# Check if OPENAI_API_KEY is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please add it to your .env file.")

# Custom TextLoader that handles encoding errors
class EncodingFriendlyTextLoader(TextLoader):
    def __init__(self, file_path, encoding=None, autodetect_encoding=True):
        super().__init__(file_path, encoding=encoding, autodetect_encoding=autodetect_encoding)
        
    def load(self):
        try:
            # Try with default behavior first
            return super().load()
        except RuntimeError as e:
            # If default fails, try with utf-8 with error handling
            try:
                with open(self.file_path, encoding='utf-8', errors='replace') as f:
                    text = f.read()
                metadata = {"source": self.file_path}
                return [Document(page_content=text, metadata=metadata)]
            except Exception as e2:
                print(f"Still failed to load {self.file_path}: {str(e2)}")
                # Return empty document with warning message
                warning = f"WARNING: Could not load file {os.path.basename(self.file_path)} due to encoding issues."
                metadata = {"source": self.file_path, "error": "encoding_issue"}
                return [Document(page_content=warning, metadata=metadata)]

# Import Document class
from langchain_core.documents import Document

print("Loading documents from cleaned_pages directory...")
# Process files manually to handle encoding errors
documents = []
for root, _, files in os.walk('./cleaned_pages'):
    for file in files:
        if file.endswith('.txt'):
            file_path = os.path.join(root, file)
            try:
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'utf-16']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            text = f.read()
                            documents.append(Document(
                                page_content=text,
                                metadata={"source": file_path}
                            ))
                        print(f"Successfully loaded {file_path} with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # If all encodings fail, read with replace error handling
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        text = f.read()
                        documents.append(Document(
                            page_content=text,
                            metadata={"source": file_path}
                        ))
                    print(f"Loaded {file_path} with replacement characters")
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
                # Include a placeholder document
                warning = f"WARNING: Could not load file {file} due to encoding issues."
                documents.append(Document(
                    page_content=warning,
                    metadata={"source": file_path, "error": "encoding_issue"}
                ))

print(f"Loaded {len(documents)} documents")

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)
texts = text_splitter.split_documents(documents)
print(f"Split into {len(texts)} chunks")

# Create embeddings using OpenAI's model
print("Creating embeddings with OpenAI's text-embedding-3-small model...")
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

# Store in FAISS
print("Building FAISS index...")
vectorstore = FAISS.from_documents(texts, embedding)

# Save to disk
print("Saving index to faiss_index_openai...")
vectorstore.save_local("faiss_index_openai")
print("Index saved successfully!")

# Optional: Test query to verify index
print("\nTesting index with a sample query...")
query = "OPT application process"
docs = vectorstore.similarity_search(query, k=2)
print(f"\nTop result for '{query}':")
print(f"Source: {docs[0].metadata.get('source', 'Unknown')}")
print(f"Content preview: {docs[0].page_content[:200]}...\n")