from typing import Any, Dict, List, Optional, Union

import chromadb
from chromadb.api.types import Metadata
from dspy import Tool
from sentence_transformers import SentenceTransformer


class ChromaDBTool(Tool):
    """Tool for interacting with ChromaDB vector database."""

    def __init__(self, collection_name: str = "default", model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize ChromaDB connection and collection.

        Args:
            collection_name: Name of the collection to use (default: "default")
            model_name: Name of the sentence transformer model to use
        """
        self.client = chromadb.HttpClient(
            host="localhost",
            port=8000,
        )
        self.model = SentenceTransformer(model_name)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self,
                     documents: List[str],
                     metadatas: Optional[List[Dict[str, Union[str, int, float, bool]]]] = None,
                     ids: Optional[List[str]] = None) -> None:
        """
        Add documents to the vector database.

        Args:
            documents: List of text documents to embed
            metadatas: Optional list of metadata dicts for each document
            ids: Optional list of IDs for each document
        """
        if ids is None:
            ids = [str(i) for i in range(len(documents))]

        if metadatas is None:
            metadatas = [{"id": str(i)} for i in range(len(documents))]

        embeddings = self.model.encode(documents).tolist()
        if not isinstance(embeddings[0], list):
            embeddings = [embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding) for embedding in embeddings]

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def query(self,
              query_text: str,
              n_results: int = 5,
              where: Optional[Dict[str, Any]] = None) -> Dict[str, List[Any]]:
        """
        Query the vector database.

        Args:
            query_text: Text to search for
            n_results: Number of results to return
            where: Optional filter conditions

        Returns:
            Dictionary containing documents, metadatas and distances
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
        return results
