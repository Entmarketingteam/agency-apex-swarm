"""Pinecone client for vector database operations."""

from typing import Dict, Any, Optional, List
from pinecone import Pinecone
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)


class PineconeClient:
    """Client for Pinecone vector database - lead deduplication and similarity search."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: str = "apex-leads",
        dimension: int = 1536  # OpenAI embedding dimension
    ):
        self.api_key = api_key or config.PINECONE_API_KEY
        self.index_name = index_name
        self.dimension = dimension
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        self._ensure_index()
    
    def _ensure_index(self):
        """Ensure the index exists, create if it doesn't."""
        try:
            # List existing indexes
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name in existing_indexes:
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Connected to existing Pinecone index: {self.index_name}")
            else:
                # Create index using new SDK
                from pinecone import ServerlessSpec
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                # Wait a moment for index to be ready
                import time
                time.sleep(2)
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Created new Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Pinecone index error: {e}")
            # Try to connect anyway if index might exist
            try:
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Connected to Pinecone index: {self.index_name}")
            except:
                raise
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(Exception,))
    def upsert_lead(
        self,
        lead_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Upsert a lead embedding into the vector database.
        
        Args:
            lead_id: Unique lead identifier
            embedding: Vector embedding of the lead
            metadata: Additional metadata to store
        
        Returns:
            Success status
        """
        try:
            # Validate embedding is a list of floats
            if not isinstance(embedding, list):
                raise ValueError(f"Embedding must be a list, got {type(embedding)}")
            
            if not embedding:
                raise ValueError("Embedding cannot be empty")
            
            # Ensure all values are floats
            embedding = [float(v) for v in embedding]
            
            # Validate lead_id is a string
            if not isinstance(lead_id, str):
                lead_id = str(lead_id)
            
            # Ensure metadata values are serializable
            clean_metadata = {}
            if metadata:
                for key, value in metadata.items():
                    # Convert non-serializable types
                    if isinstance(value, datetime):
                        clean_metadata[key] = value.isoformat()
                    elif value is None:
                        clean_metadata[key] = ""
                    else:
                        clean_metadata[key] = str(value)
            
            vectors = [{
                "id": lead_id,
                "values": embedding,
                "metadata": clean_metadata or {}
            }]
            
            self.index.upsert(vectors=vectors)
            logger.info(f"Upserted lead to Pinecone: {lead_id}")
            return True
        except Exception as e:
            logger.error(f"Pinecone upsert error: {e}")
            logger.error(f"lead_id: {lead_id}, embedding type: {type(embedding)}, embedding length: {len(embedding) if isinstance(embedding, list) else 'N/A'}")
            raise
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(Exception,))
    def search_similar(
        self,
        embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar leads.
        
        Args:
            embedding: Query embedding
            top_k: Number of results to return
            filter_dict: Optional metadata filters
        
        Returns:
            List of similar leads with scores
        """
        try:
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            matches = []
            for match in results.get("matches", []):
                matches.append({
                    "id": match.get("id"),
                    "score": match.get("score"),
                    "metadata": match.get("metadata", {})
                })
            
            logger.info(f"Found {len(matches)} similar leads")
            return matches
        except Exception as e:
            logger.error(f"Pinecone search error: {e}")
            raise
    
    def check_duplicate(self, embedding: List[float], threshold: float = 0.95) -> Optional[str]:
        """
        Check if a lead is a duplicate based on similarity threshold.
        
        Args:
            embedding: Lead embedding
            threshold: Similarity threshold (0-1)
        
        Returns:
            Duplicate lead ID if found, None otherwise
        """
        similar = self.search_similar(embedding, top_k=1)
        
        if similar and similar[0]["score"] >= threshold:
            logger.warning(f"Duplicate lead detected: {similar[0]['id']}")
            return similar[0]["id"]
        
        return None

