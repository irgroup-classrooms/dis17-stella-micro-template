"""Abstract class to hold the document collection."""

from abc import ABC, abstractmethod


class DocumentCollection(ABC):
    def __init__(self, **kwargs) -> None:
        """Initializes the document collection.

        Args:
            **kwargs: Additional keyword arguments.
        """
        self.documents = []

    @abstractmethod
    def load_documents(self, document_path: str) -> None:
        """Loads documents from the specified path.

        Args:
            document_path: Path to the document collection.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")