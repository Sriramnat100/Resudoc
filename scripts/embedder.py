import os
from dotenv import load_dotenv
load_dotenv()
from typing import List
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class Embedder:
    """
    A class to generate vector embeddings for text using OpenAI's API.
    """

    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize the Embedder.
        
        Args:
            api_key (str): OpenAI API key. If None, reads from env OPENAI_API_KEY.
            model (str): The embedding model to use. Defaults to "text-embedding-3-small".
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if self.api_key and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def normalize_text(self, text: str) -> str:
        """
        Normalizes text for embedding by removing newlines and extra whitespace.
        """
        if not text:
            return ""
        # Replace newlines with spaces (recommended by OpenAI for embeddings)
        return text.replace("\n", " ").strip()

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding vector for the given text.

        Args:
            text (str): The input text.

        Returns:
            List[float]: The embedding vector.
        """
        if not text:
            return []

        if not self.client:
            print("Warning: OpenAI client not initialized. Returning mock embedding.")
            # Return a mock vector of correct dimension (1536 for small) for testing
            return [0.0] * 1536

        try:
            text = self.normalize_text(text)
            
            response = self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def get_embeddings_from_list(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embedding vectors for a list of texts (batch processing).

        Args:
            texts (List[str]): A list of input texts.

        Returns:
            List[List[float]]: A list of embedding vectors.
        """
        if not texts:
            return []

        if not self.client:
            print("Warning: OpenAI client not initialized. Returning mock embeddings.")
            return [[0.0] * 1536 for _ in texts]

        try:
            # Normalize all texts
            normalized_texts = [self.normalize_text(t) for t in texts if t]
            
            if not normalized_texts:
                return []

            response = self.client.embeddings.create(
                input=normalized_texts,
                model=self.model
            )
            
            # Map results back to order? OpenAI preserves order.
            return [data.embedding for data in response.data]
            
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            return []

if __name__ == "__main__":
    # Simple test
    embedder = Embedder()
    vec = embedder.get_embedding("Hello world")
    print(f"Embedding length: {len(vec)}")
