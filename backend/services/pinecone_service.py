
import uuid
import logging
from typing import List, Dict, Any

from pinecone import Pinecone, ServerlessSpec

from core.config import settings



class PineconeService:
    """Service class for handling Pinecone operations"""



    def __init__(self, embedding_dimension: int = 3072):
        """Initialize PineconeService"""

        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.embedding_dimension = embedding_dimension
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.index_name)




        
    def ensure_index_exists(self) -> None:
        """Ensure the Pinecone index exists, create if it doesn't"""
        
        try:
            existing_indexes = self.pc.list_indexes().names()
            
            if self.index_name not in existing_indexes:
                logging.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logging.info(f"Index {self.index_name} created successfully")
            
            self.index = self.pc.Index(self.index_name)
            logging.info(f"Connected to index: {self.index_name}")
            
        except Exception as e:
            logging.error(f"Failed to initialize Pinecone index: {str(e)}")
            return {"status": "error", "message": f"Failed to initialize Pinecone index: {str(e)}"}




    
    def prepare_vectors(
        self, chunks: List, embeddings: List[List[float]], 
        filename: str, namespace: str
    ) -> List[Dict[str, Any]]:
        """Prepare vectors for upsert to Pinecone"""

        vectors_to_upsert = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Create unique ID for the chunk
            chunk_id = f"{filename}_{namespace}_{i}_{uuid.uuid4().hex[:8]}"
            
            # Prepare metadata
            metadata = {
                "text": chunk.page_content,
                "source": filename,
                "namespace": namespace,
                "chunk_index": i,
                "page": chunk.metadata.get("page", 0),
            }
            
            vectors_to_upsert.append({
                "id": chunk_id,
                "values": embedding,
                "metadata": metadata
            })

        return vectors_to_upsert





    def upsert_vectors(
        self, vectors: List[Dict[str, Any]], 
        namespace: str, batch_size: int = 100
    ) -> int:
        """Upsert vectors to Pinecone in batches"""

        if not self.index:
            return {"status": "error", "message": "Pinecone index not initialized"}

        
        total_upserted = 0
        
        try:
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)
                total_upserted += len(batch)
                logging.info(f"Upserted batch {i//batch_size + 1}, total: {total_upserted}")
            
            logging.info(f"Successfully upserted {total_upserted} vectors to namespace '{namespace}'")
            return {"status": "success", "total_upserted": total_upserted}
            
        except Exception as e:
            logging.error(f"Failed to upsert vectors: {str(e)}")
            return {"status": "error", "message": f"Failed to upsert vectors to Pinecone: {str(e)}"}





    async def search(self, query_vector: List[float], namespace: str, top_k: int = 5) -> List[Dict]:
        """Search for similar vectors in Pinecone index"""
        
        logging.info('Searching for relevant documents in Pinecone')
        try:
            search_results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace
            )

            
            retrieved_docs = []
            for match in search_results.matches:
                retrieved_docs.append({
                    "content": match.metadata.get("text", ""),
                    "score": match.score
                })
            
            return {"status": "success", "data": retrieved_docs}

        except Exception as e:
            logging.error(f"Pinecone search error: {e}")
            return {"status": "error", "message": f"Pinecone search error: {str(e)}"}


pinecone_service = PineconeService()
