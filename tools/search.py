import chromadb
from chromadb.utils import embedding_functions
import os
from django.conf import settings

class SearchService:
    _client = None
    _embedding_fn = None
    
    @classmethod
    def get_client(cls):
        if cls._client is None:
            # Persist data in the 'chroma_db' directory within the project
            db_path = os.path.join(settings.BASE_DIR, 'chroma_db')
            cls._client = chromadb.PersistentClient(path=db_path)
        return cls._client
    
    @classmethod
    def get_embedding_function(cls):
        if cls._embedding_fn is None:
            # Use a multilingual embedding model
            # Using paraphrase-multilingual-MiniLM-L12-v2 which is excellent for semantic search in multiple languages including Hungarian
            cls._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
        return cls._embedding_fn
    
    @classmethod
    def get_collection(cls, name="tools"):
        client = cls.get_client()
        embedding_fn = cls.get_embedding_function()
        return client.get_or_create_collection(
            name=name,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        
    @classmethod
    def clear_index(cls, models=None):
        """
        Clear the search index for specified models.
        :param models: List of model names ('tools', 'stacks', 'professions') or None for all.
        """
        client = cls.get_client()
        all_models = ['tools', 'stacks', 'professions']
        target_models = models if models else all_models
        
        for name in target_models:
            if name in all_models:
                try:
                    client.delete_collection(name)
                except ValueError:
                    # Collection doesn't exist, which is fine
                    pass

    
    @classmethod
    def generate_embedding(cls, text):
        """Generate embedding for a given text using the multilingual model."""
        embedding_fn = cls.get_embedding_function()
        # The embedding function expects a list of texts and returns a list of embeddings
        embeddings = embedding_fn([text])
        return embeddings[0]
    
    @classmethod
    def add_tools(cls, tools):
        """
        Add or update tools in the vector database.
        tools: List of Tool instances
        """
        collection = cls.get_collection("tools")
        embedding_fn = cls.get_embedding_function()
        
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
            # Generate embeddings using the embedding function
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
    def remove_tools(cls, tools):
        """
        Remove tools from the vector database.
        tools: List of Tool instances or IDs
        """
        collection = cls.get_collection("tools")
        ids = [str(t.id) if hasattr(t, 'id') else str(t) for t in tools]
        
        if ids:
            collection.delete(ids=ids)
            return len(ids)
        return 0
    
    @classmethod
    def add_professions(cls, professions):
        """
        Add or update professions in the vector database.
        professions: List of Profession instances
        """
        collection = cls.get_collection("professions")
        embedding_fn = cls.get_embedding_function()
        
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for pro in professions:
            # Construct rich text representation for embedding
            text = f"Name: {pro.name}. Description: {pro.description}. Tagline: {pro.hero_tagline}"
            
            ids.append(str(pro.id))
            documents.append(text)
            metadatas.append({
                "name": pro.name,
                "slug": pro.slug
            })
            # Generate embeddings using the embedding function
            embeddings.append(embedding_fn([text])[0])
            
        if ids:
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
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
    def remove_professions(cls, professions):
        """
        Remove professions from the vector database.
        professions: List of Profession instances or IDs
        """
        collection = cls.get_collection("professions")
        ids = [str(p.id) if hasattr(p, 'id') else str(p) for p in professions]
        
        if ids:
            collection.delete(ids=ids)
            return len(ids)
        return 0

    @classmethod
    def add_stacks(cls, stacks):
        """
        Add or update stacks in the vector database.
        stacks: List of ToolStack instances
        """
        collection = cls.get_collection("stacks")
        embedding_fn = cls.get_embedding_function()
        
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
            # Generate embeddings using the embedding function
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
    def remove_stacks(cls, stacks):
        """
        Remove stacks from the vector database.
        stacks: List of ToolStack instances or IDs
        """
        collection = cls.get_collection("stacks")
        ids = [str(s.id) if hasattr(s, 'id') else str(s) for s in stacks]
        
        if ids:
            collection.delete(ids=ids)
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
        embedding_fn = cls.get_embedding_function()
        
        # Generate query embedding using the embedding function
        query_embedding = embedding_fn([query])[0]
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        # Extract IDs
        if results['ids']:
            return results['ids'][0] # First query results
        return []
