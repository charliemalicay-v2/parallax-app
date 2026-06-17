# parallax-app

> A parallax is a displacement or difference in the apparent position of an object viewed along two different lines of sight. It perfectly describes the intentional gap between Operational and Financial data.

This repository contains the backend API for the Parallax Cost Engine, a FastAPI application designed to translate complex 103-column estimating logic into a deterministic Python pipeline, while maintaining strict database separation between financial actuals and operational commitments.

---

## 📦 Setup & Installation

Initialize the application environment and install all required dependencies using `pipenv`:

```bash
# Install the required packages
pipenv install fastapi uvicorn sqlalchemy pydantic pytest
```

## 🚀 Running the Application
To start the FastAPI development server with live-reloading enabled, run:

```bash
pipenv run uvicorn main:app --reload
```

Once the server is successfully running, you can view the interactive API documentation and test the endpoints directly in your browser:
http://127.0.0.1:8000/docs

## 🧪 Testing the Engine
This application includes a regression testing suite to enforce calculation accuracy (within a 2% tolerance) against the original estimating spreadsheet data. To execute the test pipeline, run:

```bash
pipenv run pytest -v test_engine.py
```
