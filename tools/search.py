import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
from django.conf import settings

class SearchService:
    _client = None
    _collection = None
    _model = None
    
    @classmethod
    def get_client(cls):
        if cls._client is None:
            # Persist data in the 'chroma_db' directory within the project
            db_path = os.path.join(settings.BASE_DIR, 'chroma_db')
            cls._client = chromadb.PersistentClient(path=db_path)
        return cls._client
    
    @classmethod
    def get_collection(cls, name="tools"):
        client = cls.get_client()
        return client.get_or_create_collection(name=name)
    
    @classmethod
    def get_model(cls):
        if cls._model is None:
            # Use a lightweight model for speed
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._model
    
    @classmethod
    def generate_embedding(cls, text):
        model = cls.get_model()
        return model.encode(text).tolist()
    
    @classmethod
    def add_tools(cls, tools):
        """
        Add or update tools in the vector database.
        tools: List of Tool instances
        """
        collection = cls.get_collection("tools")
        model = cls.get_model()
        
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for tool in tools:
            # We index English translation primarily
            translation = tool.translations.filter(language='en').first()
            if not translation:
                continue
                
            # Construct rich text representation for embedding
            # "Name: ... Description: ... Use Cases: ... Tags: ..."
            tags = ", ".join([t.name for t in tool.tags.all()])
            text = f"Name: {tool.name}. Description: {translation.short_description} {translation.long_description}. Use Cases: {translation.use_cases}. Tags: {tags}"
            
            ids.append(str(tool.id))
            documents.append(text)
            metadatas.append({
                "name": tool.name,
                "pricing": tool.pricing_type,
                "slug": tool.slug
            })
            embeddings.append(model.encode(text).tolist())
            
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
    def add_stacks(cls, stacks):
        """
        Add or update stacks in the vector database.
        stacks: List of ToolStack instances
        """
        collection = cls.get_collection("stacks")
        model = cls.get_model()
        
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for stack in stacks:
            # Construct rich text representation for embedding
            tools = ", ".join([t.name for t in stack.tools.all()])
            text = f"Name: {stack.name}. Tagline: {stack.tagline}. Description: {stack.description}. Tools: {tools}. Workflow: {stack.workflow_description}"
            
            ids.append(str(stack.id))
            documents.append(text)
            metadatas.append({
                "name": stack.name,
                "slug": stack.slug,
                "visibility": stack.visibility,
                "owner_id": str(stack.owner_id) if stack.owner_id else ""
            })
            embeddings.append(model.encode(text).tolist())
            
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
    def search(cls, query, n_results=20, collection_name="tools", where=None):
        """
        Search for tools or stacks using semantic search.
        Returns a list of IDs.
        """
        if not query:
            return []
            
        collection = cls.get_collection(collection_name)
        model = cls.get_model()
        
        query_embedding = model.encode(query).tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        # Extract IDs
        if results['ids']:
            return results['ids'][0] # First query results
        return []
