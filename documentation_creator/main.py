from gdrive_utils import download_drive_docs
from vector_store_utils import upload_documents_to_pinecone, run_rag, delete_documents_from_pinecone
from template_utils import build_queries, fill_template
import json
from time import sleep
import uuid

INDEX_NAME = 'project-docs'
namespace = str(uuid.uuid4())

def main(drive_link, template_id):
    
    docs = download_drive_docs(drive_link)

    document_ids = upload_documents_to_pinecone(docs, INDEX_NAME, namespace, chunk_size=2500)

    queries_by_section = build_queries(template_id)

    responses = {}
    for section, queries in queries_by_section.items():
        responses[section] = {}
        for query in queries:
            responses[section][query] = run_rag(query, INDEX_NAME, namespace)

    document = fill_template(responses, template_id)
    
    delete_documents_from_pinecone(document_ids, INDEX_NAME, namespace)

    return document

if __name__ == '__main__':
    final_doc = main("", '19FlXUYAR5bcMO9gIBUIsFhWP0EG56PYa1zSkDUFUkN4')
    print(final_doc)