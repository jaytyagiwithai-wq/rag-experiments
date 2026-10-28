from pathlib import Path
import warnings

warnings.filterwarnings(
    "ignore",
    message=r"`langchain-community` is being sunset.*",
    category=DeprecationWarning,
)

# Your other imports go below

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import re

PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"

load_dotenv(PROJECT_DIR / ".env")

chroma = chromadb.Client()
collections = chroma.get_or_create_collection(name="hybrid")

loader = TextLoader(file_path=str(DATA_DIR / "neurowave.md"), encoding="utf-8")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500 ,chunk_overlap =50,
    separators=["\n\n","\n"," "]
)

split_docs=splitter.split_documents(docs)
collections.upsert(
    ids= [f"id {i}" for i in range(len(split_docs))],
    documents=[doc.page_content for doc in split_docs],
    metadatas=[{**doc.metadata, "source": "neurowave.md"} for doc in split_docs]
)



def tokenize(text):
    return re.findall(r"\w+(?:[-.]\w+)*", text.lower()) #keeps identifer like sku-7723A together


bm25_retriever= BM25Retriever.from_documents(
    split_docs,
    preprocess_func=tokenize,
    k=5
)


query = "What is the warranty of SKU-7742M?"

#bm25_results = bm25_retriever.invoke(query)


#for rank, doc in enumerate(bm25_results, start=1):
   # print(rank, doc.metadata)
   # print(f"\n\n {doc.page_content[:100]}")

vector_store = Chroma(
    client=chroma,
    collection_name="hybrid"
)

vectore_retiever = vector_store.as_retriever(
    search_kwargs={"k":5}
)

print("\nVector results")


#combine the ranking with rpf

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vectore_retiever],
    weights=[0.5,0.5]
)

result = ensemble_retriever.invoke(query)

for i, doc in enumerate(result, start=1):
    prev = doc.page_content[:80] + "..."
    print(f"{i}. {prev}")
