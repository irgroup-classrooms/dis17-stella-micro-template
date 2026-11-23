# E-commerce Search Engine Project

This repository is the starting point (template) for your search engine. It provides a small web service (REST API) built with [FastAPI](https://fastapi.tiangolo.com/) that talks to an [Elasticsearch](https://www.elastic.co/elasticsearch) instance. **You have to implement the indexing and the search logic yourself**: look for the `TODO` comments in [`app.py`](./app.py).

**Files that you should modify:**

| File | Purpose |
| --- | --- |
| [`app.py`](./app.py) | The web service: endpoints, Elasticsearch connection, and the places you need to complete. |
| [`create_run_file.py`](./create_run_file.py) | Placeholder script to create run files in the TREC format for `trec_eval`. |
| [`.env.example`](./.env.example) | Template for the environment variables (Elasticsearch URL and index name). |
| `data/` | Put the product data here. Its contents are not tracked by git. |

You are free to add new files and dependencies to [`requirements.txt`](./requirements.txt). However, you **cannot** change the API endpoints, their parameters, or the response format.

**Other files:**

| File | Purpose |
| --- | --- |
| [`models.py`](./models.py) | Pydantic models that define the structure of the API responses. |
| [`config/api-conf.yaml`](./config/api-conf.yaml) | Titles, descriptions, and examples shown in the interactive API documentation. |
| [`Dockerfile`](./Dockerfile) | Builds the service as a Docker image. |
| [`docker-compose.yaml`](./docker-compose.yaml) | Starts the service together with Elasticsearch: `docker compose up --build`. |
| [`test/`](./test) | Unit tests. |

## Getting started

### Requirements

  - Python>=3.11

### Setup

1. Fork or clone this repository.
2. Install the dependencies: `pip install -r requirements.txt`. It is strongly recommended to use a virtual environment.
3. Start an Elasticsearch instance locally. Starting commands can be found in the course's exercises.

4. Copy `.env.example` to `.env` and adjust the variables values if needed. The service reads these variables:

   | Variable | Default | Explanation |
   | --- | --- | --- |
   | `ELASTICSEARCH_URL` | `http://localhost:9200` | Address of the Elasticsearch instance. |
   | `INDEX_NAME` | `products` | Name of the index used by the service. |

5. Start the search engine service: `python app.py`

The service listens on port `8000`. Open <http://localhost:8000> to be redirected to the interactive API documentation (routes `/docs` and `/redoc`).

### Working on the project

Make sure to record what you tried, why, what you observed, and what you decided in a lab book. It is a deliverable and the basis for your final presentation. I recommend using git and GitHub to track your work and commit often to have a history and backup of your work.

You can use the provided unit tests in [`test/`](./test) to check that your service is working correctly. You can run them with `pytest test/`, note that `test_write_run_file_uses_trec_format` and `test_write_run_file_with_no_results_creates_empty_file` are expected to fail until you implement `write_run_file` in [`create_run_file.py`](./create_run_file.py).
You can also add your own tests.

## REST endpoints

| Method | Path | Explanation |
| --- | --- | --- |
| GET | `/health` | Checks that the service is running. |
| GET | `/index` | Builds (or rebuilds) the search index from the product data. May take a while. |
| GET | `/ranking?query=<string>` | Returns the ranked results for a query. |

Parameter of `/ranking`:

| Parameter | Explanation |
| --- | --- |
| `query` | Search query, at least one character. |
| `b_online` | If true, return SERP for online search. Otherwise, return a list of tuples with document ID, rank, and score for run file. |

For online search, the ranking response is a JSON document (see [`models.py`](./models.py)):

| Field | Explanation |
| --- | --- |
| `itemlist` | Document IDs, best match first. |
| `num_found` | Number of retrieved documents. |
| `page` | Current page, starting at 0. |
| `rpp` | Results per page. |

Example:

```json
{
  "itemlist": ["doc1", "doc2", "doc3"],
  "num_found": 3,
  "page": 0,
  "rpp": 5
}
```

## Create run files

For the offline evaluation, you will use the `trec_eval` toolkit. To create run files in the TREC format, you should either complete the `create_run_file.py` script or write your own.

The TREC format is a text file with one line per retrieved document, with the following fields:

```plain
<query_id> Q0 <doc_id> <rank> <score> <run_tag>
```

Where:

  - `query_id` is the ID of the query (from the query file).
  - `Q0` is a constant.
  - `doc_id` is the ID of the retrieved document.
  - `rank` is the rank of the document for this query (starting at 1).
  - `score` is the score of the document for this query (can be any float).
  - `run_tag` is a string that identifies the run.

## Questions and Troubleshooting

If you have any questions or issues, you can ask on the course's discussion forum. Make sure to provide a detailed description of the problem, including the steps to reproduce it, any error messages, and your environment (OS, Python version, Elasticsearch version, etc.). You can also reach out by email but replies may take longer.
