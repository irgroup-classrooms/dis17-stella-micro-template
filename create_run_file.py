"""Creates a run file in the TREC format from the search engine service.

The run file produced can be evaluated with the trec_eval toolkit.


Usage:
    python create_run_file.py <query_file> <run_file> <run_tag> --service_url <service_url>
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlencode
from urllib.request import urlopen


def load_queries(path: Path) -> List[Tuple[str, str]]:
    """Loads the queries to run.

    Args:
        path: Path to the query file.

    Raises:
        FileNotFoundError: If the query file does not exist.

    Returns:
        A list of tuples (query_id, query_text).
    """
    if not path.is_file():
        raise FileNotFoundError(f"Query file not found: {path}")

    queries = []
    # TODO: Implement the logic to read the query file and populate the queries
    # list.
    return queries


def retrieve(service_url: str, query: str) -> List[Tuple[str, int, float]]:
    """Gets the ranked documents of a query from the ``/ranking`` endpoint.

    Args:
        service_url: Base URL of the search engine service.
        query: Search query.

    Returns:
        A list of tuples (doc_id, rank, score), best match first.
    """
    params = urlencode({"query": query, "b_online": "false"})
    with urlopen(f"{service_url}/ranking?{params}") as response:
        return json.load(response)["doc_list"]


def write_run_file(
    path: Path, queries_results: Dict[str, List[Tuple[str, int, float]]], run_tag: str
) -> None:
    """Writes the results of all queries to a run file in the TREC format.

    Args:
        path: Path to the output run file.
        queries_results: Dictionary mapping query IDs to search results (list
          of tuples).
        run_tag: Name of this run, without whitespace.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # TODO: Implement the logic to write the run file in the TREC format.
    # Reminder: Each line should follow the format:
    # <query_id> Q0 <doc_id> <rank> <score> <run_tag>


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments.

    Returns:
        An argparse.Namespace object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("query_file", type=Path, help="Path to the query file.")
    parser.add_argument("run_file", type=Path, help="Path to the output run file.")
    parser.add_argument("run_tag", help="Name of this run, without whitespace.")
    parser.add_argument(
        "--service_url",
        default="http://localhost:8000",
        help="Base URL of the search engine service.",
    )
    return parser.parse_args()


def main(query_file: Path, run_file: Path, run_tag: str, service_url: str) -> None:
    """Performs the retrieval for all queries and writes the results to a run file.

    Args:
        query_file: Path to the query file.
        run_file: Path to the output run file.
        run_tag: Name of this run, without whitespace.
        service_url: Base URL of the search engine service.
    """
    queries = load_queries(query_file)
    queries_results = {
        query_id: retrieve(service_url, query) for query_id, query in queries
    }
    write_run_file(run_file, queries_results, run_tag)
    print(f"Created run file at {run_file} for {len(queries_results)} queries.")


if __name__ == "__main__":
    args = parse_arguments()
    main(args.query_file, args.run_file, args.run_tag, args.service_url)
