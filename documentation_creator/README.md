# Project Documentation Generator

## Purpose
This app automates the process of generating detailed project documentation based on a provided Google Drive link containing relevant documents and a template ID. The primary purpose is to streamline the documentation creation process by leveraging RAG techniques, making it easier to compile, analyze, and format information from various sources into a cohesive document.

## Features
- **Download Documents:** Integrated with Google APIs to retrieve documents from a specified Google Drive and Doc links.
- **Upload to Pinecone:** Split documents into chunks and upload to a Pinecone index for querying.
- **Build and Execute Queries:** Construct and run queries based on a provided template that will help fill it up.
- **Generate Document:** Fill out the template with retrieved information to create a comprehensive document.
- **Cleanup:** Delete documents from Pinecone after processing.

## Caveats
- **Document Quality:** The final document's quality depends on the relevance and completeness of the provided documents.
- **Information Gaps:** Missing information in documents will be indicated with remarks in the final document.
- **Template Constraints:** Templates are best fit when they are in markdown format.

## Running the App Locally
To run the application, use the following command:
```bash
cd documentation_creator
streamlit run frontend.py
```

[UI Image](https://drive.google.com/file/d/1zgIuxhekssexvaRjRh6rV1Hkf5Y6jD7a/view?usp=sharing) 