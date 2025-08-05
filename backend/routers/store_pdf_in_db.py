
import os
import logging

from fastapi import APIRouter, UploadFile, File, Form

from core.config import settings
from services.openai_service import openai_service
from services.pinecone_service import pinecone_service
from schemas.dataclasses.namespace import NamespaceEnum
from utils.file_operations import process_file, split_and_create_embeddings



router = APIRouter()



@router.post("/store_pdf_in_db")
async def upload_pdf(
    file: UploadFile = File(...),
    namespace: NamespaceEnum = Form(...)
):
    """Upload a PDF file and process it into chunks stored in Pinecone"""

    
    try:
        # Process the uploaded file
        processing_result = await process_file(file)
        if processing_result.get("status") == "error":
            return processing_result



        # Split documents and create embeddings
        split_result = await split_and_create_embeddings(processing_result.get("documents"), openai_service)
        if split_result.get("status") == "error":
            return split_result



        # Prepare vectors for Pinecone
        vectors = pinecone_service.prepare_vectors(
            chunks=split_result.get("chunks"),
            embeddings=split_result.get("embeddings"),
            filename=file.filename,
            namespace=namespace.value
        )



        # Upsert vectors to Pinecone
        upsert_vectors_response = pinecone_service.upsert_vectors(
            vectors=vectors,
            namespace=namespace.value
        )
        if upsert_vectors_response.get("status") == "error":
            return upsert_vectors_response


        total_upserted = upsert_vectors_response.get("total_upserted")


        return {
            "status": "success",
            "content": {
                "message": "PDF processed successfully",
                "filename": file.filename,
                "namespace": namespace.value,
                "total_chunks": len(split_result.get("chunks")),
                "total_vectors_upserted": total_upserted,
                "index_name": settings.PINECONE_INDEX_NAME
            }
        }


    except Exception as e:
        logging.error(f"Error processing PDF: {str(e)}")
        return {"status": "error", "message": f"Error processing PDF: {str(e)}"}


    finally:
        # Clean up temporary file
        temp_file_path = processing_result.get("temp_file_path")
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
