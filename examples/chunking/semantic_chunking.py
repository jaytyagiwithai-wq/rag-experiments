from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
import chromadb
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"

load_dotenv(PROJECT_DIR / ".env")

chroma =chromadb.Client()

collectionA = chroma.get_or_create_collection(name="recursiveVecotreStore")
#collectionB = chroma.get_or_create_collection(name="SemanticVecotreStore")


embeddings = OpenAIEmbeddings()


loader = TextLoader(file_path=str(DATA_DIR / "neurowave.md"), encoding="utf-8")
docs = loader.load()


splitter = RecursiveCharacterTextSplitter(
    chunk_size = 400,
    chunk_overlap=50,
    separators=["\n\n","\n"," "]
)


#chunking at arbitarary points
'''
for i, chunk in enumerate(chunks,start=1):
    print(f"ids: chunk_id {i}, content: {chunk.page_content}\n\n")

'''


semantic_chunker = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=90
)


def chunk_documents(documents, strategy="semantic"):

    if strategy not in ("semantic", "recursive"):
        raise ValueError("Invalid chunking strategy")

    if strategy == "semantic":
        try:
            chunks = semantic_chunker.split_documents(documents)

            if not chunks:
                raise ValueError("Semantic chunking returned no chunks")

            print("Using semantic chunking")
            return chunks, "semantic"

        except Exception as e:
            print(f"Semantic chunking failed: {e}")
            print("Falling back to recursive chunking...")

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("No chunks generated")

    print("Using recursive chunking")
    return chunks, "recursive"




'''
print("\n Semantic Chunking \n")
for i, chunk in enumerate(sem_chunks,start=1):
    print(f"ids: chunk_id {i}, content: {chunk.page_content}\n\n")


'''


def store_chunks(collection, chunks, strategy):

    collection.upsert(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        documents=[chunk.page_content for chunk in chunks],
        metadatas=[
            {"chunk_id": f"chunk_{i}","strategy": strategy} for i, chunk in enumerate(chunks)]
    )

    print(f"Stored {len(chunks)} {strategy} chunks")


def build_knowledge_base(
    documents,
    collection,
    strategy="semantic"
):
    chunks, used_strategy = chunk_documents(documents, strategy=strategy)

    store_chunks(collection, chunks, used_strategy)

    return chunks, used_strategy


build_knowledge_base(documents=docs, collection=collectionA)

'''
collectionA.upsert(
    ids= [f"chunk_{i}" for i in range(len(chunks))],
    documents=[chunk.page_content for chunk in chunks],
    metadatas=[{"source":"neurowave.md", "chunk_id": f"chunk_{i}"} for i in range(len(chunks))]
)
collectionB.upsert(
    ids= [f"chunk_{i}" for i in range(len(chunks))],
    documents=[chunk.page_content for chunk in chunks],
    metadatas=[{"source":"neurowave.md", "chunk_id": f"chunk_{i}"} for i in range(len(chunks))]

)
'''

query_text = [
    "A customer owns SKU-7742M and connects SKU-9008G to it. Can two PCs connected to the switch communicate at Gigabit speed, and what happens to traffic passing through the router?",

    "A customer purchases an Aether Mini and Beacon E2 together. Do they qualify for free standard shipping, and can they use mesh pairing?",

    "A customer using SKU-7742X experiences gaming lag while their family streams 4K videos. What configuration changes should they make, and why wouldn't the same solution work on SKU-7742M?"
]

def test_retrieval(query, collection):
    result = collection.query(
        query_texts=query,
        n_results=1
    )
    return result


print("\n\nRetrieval..\n")
res= test_retrieval(query=query_text, collection=collectionA)
for doc in res["documents"]:
    print(f"{doc[0]} \n")
