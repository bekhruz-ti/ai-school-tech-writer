from gdrive_utils import fetch_all_documents
from vector_store_utils import upload_documents_to_pinecone, run_rag, delete_documents_from_pinecone, delete_all_documents_from_pinecone
from template_utils import build_queries, fill_template
import json

INDEX_NAME = 'project-documents'
def main(drive_link, template_id):

    files = fetch_all_documents(drive_link)

    document_ids = upload_documents_to_pinecone(files, INDEX_NAME)
    
    delete_documents_from_pinecone(document_ids, INDEX_NAME)
    delete_all_documents_from_pinecone(INDEX_NAME)
    return
    queries_by_section = build_queries(template_id)
    print(json.dumps(queries_by_section, indent=2))
    responses = {}
    for section, queries in queries_by_section.items():
        responses[section] = {}
        for query in queries:
            responses[section][query] = run_rag(query, INDEX_NAME)

    document = fill_template(responses, template_id)
    print(document)
    return document

if __name__ == '__main__':
    main("1pvmioD9xQ7vGdSztlvkpmk_R4C2rVSvf", '19FlXUYAR5bcMO9gIBUIsFhWP0EG56PYa1zSkDUFUkN4')