"""Tests of the REST API contract. Elasticsearch is mocked, so no server is needed."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import app as app_module


@pytest.fixture
def es(monkeypatch):
    """A reachable Elasticsearch mock whose index exists."""
    client = MagicMock()
    client.ping.return_value = True
    client.indices.exists.return_value = True
    monkeypatch.setattr(app_module, "es_client", client)
    return client


@pytest.fixture
def client():
    return TestClient(app_module.app, follow_redirects=False)


def test_root_redirects_to_docs(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["location"] == "/docs"


def test_health_returns_plain_text(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == "Service is running!"


def test_health_does_not_need_elasticsearch(client, monkeypatch):
    unreachable = MagicMock()
    unreachable.ping.return_value = False
    monkeypatch.setattr(app_module, "es_client", unreachable)
    assert client.get("/health").status_code == 200


def test_index_succeeds_when_elasticsearch_is_up(client, es):
    assert client.get("/index").status_code == 200


def test_index_returns_503_when_elasticsearch_is_down(client, es):
    es.ping.return_value = False
    assert client.get("/index").status_code == 503


@pytest.mark.parametrize("params", [{}, {"query": ""}])
def test_ranking_rejects_missing_or_empty_query(client, es, params):
    response = client.get("/ranking", params=params)
    assert response.status_code == 422
    es.ping.assert_not_called()


def test_ranking_rejects_invalid_b_online(client, es):
    assert (
        client.get(
            "/ranking", params={"query": "shoes", "b_online": "maybe"}
        ).status_code
        == 422
    )


def test_ranking_returns_503_when_elasticsearch_is_down(client, es):
    es.ping.return_value = False
    response = client.get("/ranking", params={"query": "shoes"})
    assert response.status_code == 503
    es.indices.exists.assert_not_called()


def test_ranking_returns_404_when_index_is_missing(client, es):
    es.indices.exists.return_value = False
    response = client.get("/ranking", params={"query": "shoes"})
    assert response.status_code == 404


def test_ranking_checks_the_configured_index(client, es):
    client.get("/ranking", params={"query": "shoes"})
    es.indices.exists.assert_called_once_with(index=app_module.ES_INDEX_NAME)


def test_ranking_online_response_is_consistent(client, es):
    response = client.get("/ranking", params={"query": "shoes", "b_online": "true"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"itemlist", "num_found", "page", "rpp"}
    assert body["num_found"] == len(body["itemlist"])


@pytest.mark.parametrize(
    "params", [{"query": "shoes"}, {"query": "shoes", "b_online": "false"}]
)
def test_ranking_offline_response_is_run_file_ready(client, es, params):
    response = client.get("/ranking", params=params)
    assert response.status_code == 200
    doc_list = response.json()["doc_list"]
    assert [rank for _, rank, _ in doc_list] == list(range(1, len(doc_list) + 1))
    scores = [score for _, _, score in doc_list]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize(
    "query", ["running shoes & socks", "größe 42", "a" * 1000, "名前", "100%"]
)
def test_ranking_accepts_unusual_queries(client, es, query):
    assert client.get("/ranking", params={"query": query}).status_code == 200


def test_openapi_documents_all_endpoints(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert {"/health", "/index", "/ranking"} <= set(paths)
