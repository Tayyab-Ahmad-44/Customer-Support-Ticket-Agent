
import logging
import tempfile

from fastapi import UploadFile, File
from langchain_community.document_loaders import PyPDFLoader



async def process_file(file: UploadFile = File(...),):
    """Process the uploaded PDF file and return its content as documents."""

    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return {"status": "error", "message": "Only PDF files are allowed"}


        temp_file_path = None

        
        # Create temporary file to store uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        

        # Load PDF
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        if not documents:
            return {"status": "error", "message": "No content could be extracted from the PDF"}


        return {"status": "success", "documets": documents, "temp_file_path": temp_file_path}


    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        return {"status": "error", "message": f"Failed to process file: {str(e)}"}





async def split_and_create_embeddings(documents, openai_service):
    """Split documents into chunks and create embeddings using OpenAI service"""
    
    try:
        # Split documents into chunks
        chunks = openai_service.text_splitter.split_documents(documents)
        
        if not chunks:
            return {"status": "error", "message": "No chunks could be created from the document"}
        

        # Generate embeddings for all chunks
        logging.info(f"Generating embeddings for {len(chunks)} chunks")
        chunk_embeddings = []
        for chunk in chunks:
            embedding = openai_service.embeddings.embed_query(chunk.page_content)
            chunk_embeddings.append(embedding)


        return {"status": "success", "chunks": chunks, "embeddings": chunk_embeddings}

    except Exception as e:
        logging.error(f"Failed to split and create embeddings: {str(e)}")
        return {"status": "error", "message": f"Failed to process document: {str(e)}"}