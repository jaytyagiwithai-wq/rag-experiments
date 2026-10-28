from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import chromadb

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"

load_dotenv(PROJECT_DIR / ".env")

import os
import chromadb
from dotenv import load_dotenv

load_dotenv(PROJECT_DIR / ".env")

chroma = chromadb.CloudClient(
    api_key=os.environ["CHROMA_API_KEY"],
    tenant=os.environ["CHROMA_TENANT"],
    database=os.environ["CHROMA_DATABASE"],
)
collection = chroma.get_or_create_collection(name="rag_experiments_aurora")


def create_kb():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500 ,chunk_overlap =50
    )
    loader = TextLoader(file_path=str(DATA_DIR / "BASE.md"),encoding="utf-8")
    docs = loader.load()

    chunks = splitter.split_documents(documents=docs)


    collection.upsert(
        ids= [f"aurora_chunk_{i}" for i in range(len(chunks))],
        documents=[chunk.page_content for chunk in chunks],
        metadatas=[
            {"source":"BASE.md", "chunk":i} for i in range(len(chunks))
        ]
    )

    #for i,chunk in enumerate(chunks,start=1):
    #    print(f"Id: {i} | Content: {chunk.page_content} \n MetaData: {chunk.metadata}\n")

def retrieve_docs(question: str):
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    return "\n\n".join(results["documents"][0])

def basic_rag():
     retriever = RunnableLambda(retrieve_docs)


     llm = ChatOpenAI(
                    model="gpt-4.1-mini",
                    temperature=0.2
                )
     prompt = ChatPromptTemplate.from_messages([
          (
        "system",
        """You are a research assistant.

        Answer the user's question using only the
        provided context.

        If the answer is not in the context,
        say you don't know.

        Context:
        {context}
        """
    ),
    ("human", "{question}")
])

     rag_chain = (
         {
             "context":retriever,
             "question":RunnablePassthrough()

         }
         | prompt
         | llm
         | StrOutputParser()
     )

     ans = rag_chain.invoke("Why was ReefWatch unable to detect anomalies from buoy A-07 during the August 9 storm, and how was the issue resolved?")
     print(f"Question: Why was ReefWatch unable to detect anomalies from buoy A-07 during the August 9 storm, and how was the issue resolved? \n\n Answer: {ans}" )

if __name__ == "__main__":
    create_kb()
    basic_rag()
