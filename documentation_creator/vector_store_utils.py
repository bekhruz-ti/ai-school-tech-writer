from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter
import uuid

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

def upload_documents_to_pinecone(doc_dict, index_name):
    # Initialize the text splitter and embedding model
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
    
    # Process each document
    all_documents = []
    document_ids = []
    for doc_id, doc_info in doc_dict.items():
        content = doc_info['content']
        metadata = doc_info['metadata']
        
        # Split the document into chunks
        chunks = text_splitter.split_text(content)
        
        # Create Document objects for each chunk and generate unique IDs
        for chunk in chunks:
            unique_id = str(uuid.uuid4())  # Generate a unique ID for each chunk
            document = Document(page_content=chunk, metadata=metadata, id=unique_id)
            all_documents.append(document)
            document_ids.append(unique_id)
    
    PineconeVectorStore.from_documents(documents=all_documents, embedding=embeddings, index_name=index_name)
    
    print(f"Going to add {len(all_documents)} chunks to Pinecone")
    return document_ids

def delete_documents_from_pinecone(document_ids, index_name):
    # Initialize Pinecone Vector Store
    vector_store = PineconeVectorStore(index_name=index_name, embedding=OpenAIEmbeddings(model=EMBEDDINGS_MODEL))
    
    # Delete documents by IDs
    vector_store.delete(ids=document_ids)
    print(f"Deleted {len(document_ids)} documents from Pinecone index '{index_name}'")

def delete_all_documents_from_pinecone(index_name):
    vector_store = PineconeVectorStore(index_name=index_name, embedding=OpenAIEmbeddings(model=EMBEDDINGS_MODEL))
    vector_store.delete_index()
    vector_store.create_index()
