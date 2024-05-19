import streamlit as st
from main import main

def run_app():
    st.title("Google Drive and Docs Processor")

    drive_folder_id = st.text_input("Enter the Drive folder ID:", "")

    template_doc_id = st.text_input("Enter the Google Doc ID:", "")

    st.info("Please share the project folder and template doc with this email: the-brain@the-brain-401806.iam.gserviceaccount.com")

    if st.button("Submit"):
        if drive_folder_id and template_doc_id:
            try:
                result = main(drive_folder_id, template_doc_id)
                st.text_area("Result:", value=result, height=300)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter both a Drive folder ID and a Google Doc ID.")

if __name__ == "__main__":
    run_app()