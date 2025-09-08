# dtar-dealership

Prototype implementation of the dtar dealership project. This repository currently
contains a minimal FastAPI service with endpoints for searching listings, retrieving
listing details, and creating price alerts. Listings include a simple deal score
computed against similar vehicles in the sample dataset.

The `/search` endpoint supports filtering by make, model, year, price, and mileage
ranges to narrow down results.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the tests:

```bash
pytest
```

Start the API server:

```bash
uvicorn api.main:app --reload
```

Open a browser to `http://localhost:8000` to use a minimal web interface for
running searches against the API.

