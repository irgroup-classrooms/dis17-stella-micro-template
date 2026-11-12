"""Abstract search engine class."""

from abc import ABC, abstractmethod
from elasticsearch import Elasticsearch
from typing import Any, Dict, List

class SearchEngine(ABC):

    def __init__(self, index_name: str, es_client: Elasticsearch, **kwargs) -> None:
        """Initializes the search engine.
        
        Args:
            index_name: Name of the index to use.
            es_client: Elasticsearch client instance.
            **kwargs: Additional keyword arguments.
        """
        self.index_name = index_name
        self.es_client = es_client
    
    @abstractmethod
    def index(self, documents: List[Any], **kwargs) -> None:
        """Indexes the given documents into the search engine.
        
        Args:
            documents: List of documents to index.
            **kwargs: Additional keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def retrieve(self, query: str, **kwargs) -> Dict[str, Any]:
        """Retrieves documents based on the given query.
        
        Args:
            query: Search query string.
            **kwargs: Additional keyword arguments.
        
        Raises:
            NotImplementedError: If the method is not implemented in a subclass.

        Returns:
            A dictionary as follows:
                {
                    "query": query,
                    "retrieved_documents": List of retrieved documents,
                    "num_found": Total number of documents found
                }
        """
        raise NotImplementedError(
            "Subclasses must implement this method. Delete this raise in your"
            " implementation."
        )

        retrieved_documents = []

        return {
            "query": query,
            "retrieved_documents": retrieved_documents,
            "num_found": len(retrieved_documents),
        }



