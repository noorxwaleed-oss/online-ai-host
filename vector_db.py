import uuid
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import EMBEDDING_MODEL

def get_embedding_func():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def create_vectorstore(chunks, embedding_func, vectorstore_path):
    ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks]
    unique_ids, unique_chunks = set(), []
    for chunk, id in zip(chunks, ids):
        if id not in unique_ids:
            unique_ids.add(id)
            unique_chunks.append(chunk)

    vectorstore = Chroma.from_documents(
        documents=unique_chunks,
        ids=list(unique_ids),
        embedding=embedding_func,
        persist_directory=vectorstore_path
    )
    return vectorstore