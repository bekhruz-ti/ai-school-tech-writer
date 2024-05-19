from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter
import uuid
import os
from pinecone import Pinecone
from openai import OpenAI

EMBEDDINGS_MODEL="text-embedding-3-large"
def run_rag(query, index_name):
    embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)

    document_vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    retriever = document_vectorstore.as_retriever()

    context_documents = retriever.get_relevant_documents(query)
    context = " ".join([doc.page_content for doc in context_documents])

    template = PromptTemplate(template="{query} Context: {context}", input_variables=["query", "context"])
    print(query, context)
    prompt_with_context = template.invoke({"query": query, "context": context})

    llm = ChatOpenAI(temperature=0.7)
    answer = llm.invoke(prompt_with_context)

    return answer

def upload_documents_to_pinecone(doc_dict, index_name, namespace, chunk_size = 2000):
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)
    client = OpenAI()

    all_documents = []
    document_ids = []
    for doc_id, doc_info in doc_dict.items():
        content = doc_info['content']
        metadata = doc_info['metadata']
        
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        
        for chunk in chunks:
            unique_id = str(uuid.uuid4())  # Generate a unique ID for each chunk
            embedding = client.embeddings.create(
                model=EMBEDDINGS_MODEL,
                input=chunk,
                encoding_format="float"
            )

            document = {
                "id": unique_id,
                "values": embedding.data[0].embedding,
                "metadata": metadata
            }
            all_documents.append(document)
            document_ids.append(unique_id)
    
    upsert_response = index.upsert(
        vectors=all_documents,
        namespace=namespace
    )
    return document_ids

# def delete_documents_from_pinecone(document_ids, index_name):
#     vector_store = PineconeVectorStore(index_name=index_name, embedding=OpenAIEmbeddings(model=EMBEDDINGS_MODEL))
#     vector_store.delete(ids=document_ids)
#     print(f"Deleted {len(document_ids)} documents from Pinecone index '{index_name}'")


def delete_documents_from_pinecone(document_ids, index_name, namespace):
    print(f"Pinecone Deleting IDs: {document_ids}")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(name=index_name)
    response = index.delete(ids=document_ids, namespace=namespace)