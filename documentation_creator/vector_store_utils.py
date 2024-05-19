from langchain_text_splitters import CharacterTextSplitter
import uuid
import os
from pinecone import Pinecone
from openai import OpenAI
from typing import List, Dict, Any, Union, Optional
from prompts import INFERENCE_PROMPT
import re
import json

EMBEDDINGS_MODEL="text-embedding-3-large"

def extract_json_response(text):
    matches = re.findall(r"```json(.*?)```", text, re.DOTALL)

    if len(matches) == 0:
        matches = re.findall(r"```(.*?)```", text, re.DOTALL)
        if len(matches) == 0:
            return None 
        elif len(matches) > 1:
            raise Exception("Found more than 1 json string.")

    json_string = matches[0]
    return json_string

def str_2_json(_str: str) -> str:
    try:
        return json.loads(extract_json_response(_str))
    except:
        return json.loads(_str) 
def openai_embeddings(text: str) -> List[float]:
    client = OpenAI()
    embeddings = client.embeddings.create(
                    model=EMBEDDINGS_MODEL,
                    input=text,
                    encoding_format="float"
                )
    return embeddings.data[0].embedding

def openai_call(system_message, user_message, history: List[Dict[str, Any]] = [], model: str = 'gpt-4-turbo', is_json=False) -> Union[dict, str]:
    client = OpenAI()

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            *history,
            {"role": "user", "content": user_message}
        ]
    )
    response = completion.choices[0].message.content
    return str_2_json(response) if is_json else response

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