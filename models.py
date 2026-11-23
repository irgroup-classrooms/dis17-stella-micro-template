"""Pydantic models for the API responses."""

from typing import List, Tuple

from pydantic import BaseModel, Field


class RetrievalResponse(BaseModel):
    """Ranked results for a query ordered by relevance."""

    itemlist: List[str] = Field(
        ...,
        description="List of ranked document IDs based on relevance.",
        examples=[["doc1", "doc2", "doc3"]],
    )
    num_found: int = Field(
        ...,
        ge=0,
        description="Total number of documents retrieved for the query.",
        examples=[3],
    )
    page: int = Field(
        default=0,
        ge=0,
        description="Current page number of the results (0-based).",
        examples=[0],
    )
    rpp: int = Field(
        default=5,
        ge=1,
        description="Number of results per page.",
        examples=[5],
    )


class RunRetrievalResponse(BaseModel):
    """Ranked results for a query ordered by relevance to save in a run file."""

    doc_list: List[Tuple[str | int, int, float]] = Field(
        ...,
        description="List of tuples containing document ID, rank, and score.",
        examples=[[(1, 1, 0.95), (2, 2, 0.90), (3, 3, 0.85)]],
    )
