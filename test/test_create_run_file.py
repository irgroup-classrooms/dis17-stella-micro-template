"""Tests of the run file creation script."""

import io
import json
from urllib.parse import parse_qs, urlparse

import pytest

import create_run_file


def fake_urlopen(payload, calls):
    def urlopen(url):
        calls.append(url)
        return io.BytesIO(json.dumps(payload).encode())

    return urlopen


def test_load_queries_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_run_file.load_queries(tmp_path / "missing.tsv")


def test_retrieve_requests_run_file_results(monkeypatch):
    calls = []
    payload = {"doc_list": [["d1", 1, 2.5], ["d2", 2, 1.0]]}
    monkeypatch.setattr(create_run_file, "urlopen", fake_urlopen(payload, calls))

    results = create_run_file.retrieve("http://service:8000", "running shoes")

    url = urlparse(calls[0])
    assert (url.scheme, url.netloc, url.path) == ("http", "service:8000", "/ranking")
    assert parse_qs(url.query) == {"query": ["running shoes"], "b_online": ["false"]}
    assert results == payload["doc_list"]


def test_retrieve_encodes_special_characters(monkeypatch):
    calls = []
    monkeypatch.setattr(
        create_run_file, "urlopen", fake_urlopen({"doc_list": []}, calls)
    )

    create_run_file.retrieve("http://service:8000", "socks & shoes=100%")

    assert parse_qs(urlparse(calls[0]).query)["query"] == ["socks & shoes=100%"]


def test_retrieve_handles_no_results(monkeypatch):
    monkeypatch.setattr(create_run_file, "urlopen", fake_urlopen({"doc_list": []}, []))
    assert create_run_file.retrieve("http://service:8000", "nothing") == []


def test_write_run_file_uses_trec_format(tmp_path):
    run_file = tmp_path / "nested" / "run.txt"
    results = {
        "q1": [("d1", 1, 2.5), ("d2", 2, 1.0)],
        "q2": [("d3", 1, 0.7)],
    }

    create_run_file.write_run_file(run_file, results, "baseline")

    rows = [line.split() for line in run_file.read_text().splitlines()]
    assert [(r[0], r[1], r[2], r[3], r[5]) for r in rows] == [
        ("q1", "Q0", "d1", "1", "baseline"),
        ("q1", "Q0", "d2", "2", "baseline"),
        ("q2", "Q0", "d3", "1", "baseline"),
    ]
    assert [float(r[4]) for r in rows] == [2.5, 1.0, 0.7]


def test_write_run_file_with_no_results_creates_empty_file(tmp_path):
    run_file = tmp_path / "run.txt"
    create_run_file.write_run_file(run_file, {"q1": []}, "baseline")
    assert run_file.read_text() == ""


def test_main_runs_every_query_and_writes_the_run_file(tmp_path, monkeypatch):
    queries = [("q1", "running shoes"), ("q2", "red dress")]
    retrieved, written = [], {}
    monkeypatch.setattr(create_run_file, "load_queries", lambda path: queries)
    monkeypatch.setattr(
        create_run_file,
        "retrieve",
        lambda url, query: retrieved.append((url, query)) or [(query, 1, 1.0)],
    )
    monkeypatch.setattr(
        create_run_file,
        "write_run_file",
        lambda path, results, tag: written.update(path=path, results=results, tag=tag),
    )

    create_run_file.main(
        tmp_path / "q.tsv", tmp_path / "run.txt", "tag", "http://service:8000"
    )

    assert retrieved == [
        ("http://service:8000", "running shoes"),
        ("http://service:8000", "red dress"),
    ]
    assert written["path"] == tmp_path / "run.txt"
    assert written["tag"] == "tag"
    assert list(written["results"]) == ["q1", "q2"]
