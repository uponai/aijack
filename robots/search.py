"""
ChromaDB search integration for robots.
"""

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class RobotSearchService:
    """Service for indexing and searching robots in ChromaDB."""
    
    _client = None
    _embedding_fn = None
    
    @classmethod
    def get_client(cls):
        """Get or create ChromaDB client."""
        if not CHROMADB_AVAILABLE:
            return None
        if cls._client is None:
            # Consistent path with tools/search.py
            from django.conf import settings
            import os
            db_path = os.path.join(settings.BASE_DIR, 'chroma_db')
            cls._client = chromadb.PersistentClient(path=db_path)
        return cls._client
    
    @classmethod
    def get_embedding_function(cls):
        """Get or create embedding function."""
        if not CHROMADB_AVAILABLE:
            return None
        if cls._embedding_fn is None:
            cls._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
        return cls._embedding_fn
    
    @classmethod
    def get_collection(cls, collection_name="robots"):
        """Get or create a collection."""
        client = cls.get_client()
        if client is None:
            return None
        embedding_fn = cls.get_embedding_function()
        return client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_fn
        )
    
    @classmethod
    def add_robots(cls, robots):
        """Add or update robots in the vector database."""
        collection = cls.get_collection()
        if collection is None:
            return 0
        
        embedding_fn = cls.get_embedding_function()
        if embedding_fn is None:
            return 0
        
        ids, documents, metadatas, embeddings = [], [], [], []
        
        for robot in robots:
            # Build rich text for embedding
            text_parts = [
                f"Name: {robot.name}",
                f"Company: {robot.company.name}",
                f"Description: {robot.short_description}",
            ]
            
            if robot.long_description:
                text_parts.append(robot.long_description[:500])
            
            if robot.use_cases:
                text_parts.append(f"Use Cases: {robot.use_cases}")
            
            if robot.pros:
                text_parts.append(f"Pros: {robot.pros}")
            
            text_parts.append(f"Type: {robot.get_robot_type_display()}")
            text_parts.append(f"Target: {robot.get_target_market_display()}")
            
            text = " ".join(text_parts)
            
            ids.append(str(robot.id))
            documents.append(text)
            metadatas.append({
                "name": robot.name,
                "company": robot.company.name,
                "robot_type": robot.robot_type,
                "target_market": robot.target_market,
                "slug": robot.slug,
                "entity_type": "robot"
            })
            embeddings.append(embedding_fn([text])[0])
        
        if ids:
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            return len(ids)
        return 0
    
    @classmethod
    def remove_robots(cls, robots):
        """Remove robots from the vector database."""
        collection = cls.get_collection()
        if collection is None:
            return 0
        
        ids = []
        for r in robots:
            if hasattr(r, 'id'):
                ids.append(str(r.id))
            else:
                ids.append(str(r))
        
        if ids:
            try:
                collection.delete(ids=ids)
                return len(ids)
            except Exception:
                pass
        return 0
    
    @classmethod
    def search(cls, query, n_results=10, where=None):
        """Search for robots by query."""
        collection = cls.get_collection()
        if collection is None:
            return []
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            if results and results.get('ids') and results['ids'][0]:
                return [int(id) for id in results['ids'][0]]
        except Exception:
            pass
        
        return []
