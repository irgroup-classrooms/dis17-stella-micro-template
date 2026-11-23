"""Search microservice.

API configuration is in ``config/api-conf.yaml``.

Usage:
    python app.py
    OR
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
"""

import os
from pathlib import Path
from typing import Annotated, Any, Dict

import uvicorn
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from starlette import status
from fastapi.responses import PlainTextResponse, RedirectResponse

from models import RetrievalResponse, RunRetrievalResponse
from elasticsearch import Elasticsearch

load_dotenv()

CONFIG_PATH = Path(__file__).parent / "config" / "api-conf.yaml"


def load_config(path: Path) -> Dict[str, Any]:
    """Loads the API configuration from a YAML file.

    Args:
        path: YAML file path.

    Raises:
        FileNotFoundError: If the YAML file does not exist.

    Returns:
        A dictionary containing the API configuration.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)["api"]


config = load_config(CONFIG_PATH)


app = FastAPI(
    title=config["title"],
    summary=config.get("summary"),
    description=config["description"],
    version=config["version"],
    contact=config.get("contact"),
    openapi_tags=config.get("tags"),
    docs_url=config["docs"]["swagger_ui"],
    redoc_url=config["docs"]["redoc"],
    openapi_url=config["docs"]["openapi_json"],
)

es_client = Elasticsearch(os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200"))
ES_INDEX_NAME = os.environ.get("INDEX_NAME", "products")


@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    """Redirects the root path to the Swagger UI."""
    return RedirectResponse(
        url=config["docs"]["swagger_ui"], status_code=status.HTTP_302_FOUND
    )


@app.get("/health", **config["endpoints"]["health"])
def test() -> PlainTextResponse:
    """Checks if the service is running."""
    return PlainTextResponse("Service is running!")


@app.get("/index", **config["endpoints"]["index"])
def index() -> PlainTextResponse:
    """Triggers (re)indexing of all documents."""
    if not es_client.ping():
        raise HTTPException(
            status_code=503,
            detail="Elasticsearch is not reachable. Check the URL in the environment variables.",
        )

    # TODO: Implement the actual indexing logic here.
    return PlainTextResponse(
        "No documents indexed yet. Implement the indexing logic in the /index endpoint and change this message.",
        status_code=status.HTTP_200_OK,
    )


@app.get("/ranking", **config["endpoints"]["ranking"])
def retrieve(
    query: Annotated[
        str,
        Query(min_length=1, description="Search query.", examples=["running shoes"]),
    ],
    b_online: Annotated[
        bool,
        Query(description="If true, return SERP for online search.", examples=[True]),
    ] = False,
) -> RetrievalResponse | RunRetrievalResponse:
    """Retrieves ranked results for a query."""
    if not es_client.ping():
        raise HTTPException(
            status_code=503,
            detail="Elasticsearch is not reachable. Check the URL in the environment variables.",
        )

    if not es_client.indices.exists(index=ES_INDEX_NAME):
        raise HTTPException(status_code=404, detail="Index not found.")

    # TODO: Implement the actual search logic here.
    results = []  # TODO: Replace with actual search results from Elasticsearch.

    if b_online:
        return RetrievalResponse(itemlist=results, num_found=len(results))
    return RunRetrievalResponse(doc_list=results)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
