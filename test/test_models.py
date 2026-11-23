"""Tests of the response models."""

import pytest
from pydantic import ValidationError

from models import RetrievalResponse, RunRetrievalResponse


def test_retrieval_response_defaults():
    response = RetrievalResponse(itemlist=["a", "b"], num_found=2)
    assert (response.page, response.rpp) == (0, 5)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"itemlist": ["a"]},
        {"num_found": 1},
        {"itemlist": None, "num_found": 0},
        {"itemlist": ["a"], "num_found": -1},
        {"itemlist": ["a"], "num_found": 1, "page": -1},
        {"itemlist": ["a"], "num_found": 1, "rpp": 0},
    ],
)
def test_retrieval_response_rejects_invalid_values(kwargs):
    with pytest.raises(ValidationError):
        RetrievalResponse(**kwargs)


def test_run_retrieval_response_accepts_str_and_int_ids():
    response = RunRetrievalResponse(doc_list=[("doc1", 1, 0.9), (2, 2, 0.5)])
    assert [doc_id for doc_id, _, _ in response.doc_list] == ["doc1", 2]


def test_run_retrieval_response_accepts_empty_list():
    assert RunRetrievalResponse(doc_list=[]).doc_list == []


@pytest.mark.parametrize(
    "doc_list", [None, [("doc1", 1)], [("doc1", "first", 0.9)], [("doc1", 1, "high")]]
)
def test_run_retrieval_response_rejects_invalid_values(doc_list):
    with pytest.raises(ValidationError):
        RunRetrievalResponse(doc_list=doc_list)
