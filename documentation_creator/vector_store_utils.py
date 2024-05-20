from langchain_text_splitters import CharacterTextSplitter
import uuid
import os
from pinecone import Pinecone
from openai import OpenAI
from typing import List, Dict, Any, Union, Optional
from prompts import INFERENCE_PROMPT
from general_utils import openai_call, openai_embeddings
import re
import json


def run_rag(query, index_name, namespace):

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)

    embedded_query = openai_embeddings(query)

    res = index.query(vector=embedded_query, 
        top_k=2, 
        namespace=namespace,
        include_metadata=True)

    context = "\n\n".join([f"<h1>{doc['metadata']['name']}</h1>\n{doc['metadata']['content']}" for doc in res['matches']])

    answer = openai_call(
        INFERENCE_PROMPT.format(information = context),
        query,
        is_json = True
    )

    return answer['Answer']

def upload_documents_to_pinecone(doc_dict, index_name, namespace, chunk_size = 2000):
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_size*0.1)
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)

    all_documents = []
    document_ids = []
    for doc_id, doc_info in doc_dict.items():
        chunks = text_splitter.split_text(doc_info['content'])
        
        for chunk in chunks:
            unique_id = str(uuid.uuid4())  # Generate a unique ID for each chunk
            all_documents.append({
                "id": unique_id,
                "values": openai_embeddings(chunk),
                "metadata": {
                    "content": doc_info['content'],
                    **doc_info['metadata']
                }
            })
            document_ids.append(unique_id)
    
    upsert_response = index.upsert(
        vectors=all_documents,
        namespace=namespace
    )
    return document_ids

def delete_documents_from_pinecone(document_ids, index_name, namespace):
    print(f"Pinecone Deleting IDs: {document_ids}")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(name=index_name)
    response = index.delete(ids=document_ids, namespace=namespace)

if __name__=='__main__':
    result = run_rag('What is the Brain project?', 'project-docs', 'dummy')
    print(json.dumps(result))