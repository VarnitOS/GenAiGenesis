import cohere
from config.settings import COHERE_API_KEY

class CohereClient:
    """Singleton Cohere client to manage API interactions"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CohereClient, cls).__new__(cls)
            cls._instance.client = cohere.Client(COHERE_API_KEY)
        return cls._instance
    
    def embed(self, texts, model=None, input_type="search_document"):
        """Generate embeddings for texts using Cohere's embed endpoint"""
        if model is None:
            from config.settings import EMBED_MODEL
            model = EMBED_MODEL
            
        response = self.client.embed(
            texts=texts,
            model=model,
            input_type=input_type
        )
        return response.embeddings
    
    def chat(self, message, model=None, preamble=None, documents=None, temperature=0.7):
        """Generate chat responses using Cohere's chat endpoint"""
        if model is None:
            from config.settings import CHAT_MODEL
            model = CHAT_MODEL
            
        return self.client.chat(
            message=message,
            model=model,
            preamble=preamble,
            documents=documents,
            temperature=temperature
        )
    
    def rerank(self, query, documents, top_n=5, model=None):
        """Rerank documents based on relevance to query"""
        if model is None:
            from config.settings import RERANK_MODEL
            model = RERANK_MODEL
            
        return self.client.rerank(
            query=query,
            documents=documents,
            top_n=top_n,
            model=model
        )
    
    def classify(self, inputs, examples, model=None):
        """Classify text into categories using examples"""
        if model is None:
            from config.settings import CHAT_MODEL
            model = CHAT_MODEL
            
        return self.client.classify(
            inputs=inputs,
            examples=examples
        )

# Create a global instance for easy import
cohere_client = CohereClient() 