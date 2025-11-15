# BeerOverflow
2025 Commerzbank Collabothon.

To initialize the database, run the following command:'

```bash
poetry run python cli.py init-db
```

This will set up the necessary database schema for the application.

## Features
- Indexing pdf
```bash
 poetry run python cli.py index-pdf "C:\Users\test-tw\PycharmProjects\BeerOverflow\data\1738294282-2-deposit-terms-and-conditions-mb-i-m-182-5-rev-jan-21-2.pdf"                                                                    
```
- Listing indexed documents
```bash
poetry run python cli.py list-products  
```
- Asking questions
```bash
poetry run python cli.py ask "What is the deposit amount for a 0.5l bottle?" 
```
- Comparing products
```bash
poetry run python cli.py compare "1738294282-2-deposit-terms-and-conditions-mb-i-m-182-5-rev-jan-21-2.pdf" "1738294282-3-deposit-terms-and-conditions-mb-i-m-182-5-rev-jan-21-3.pdf"
```
- NER-based question answering
```bash
poetry run python cli.py ner-qa "1738294282-2-deposit-terms-and-conditions-mb-i-m-182-5-rev-jan-21-2.pdf" "What is the deposit amount for a 0.5l bottle?"
```

 ## Doc Analysis Service

  The doc_analysis service exposes a small REST API for working with PDFs:

  - GET /health – basic health check
  - GET /products – list structured products derived from indexed PDFs
  - POST /index-pdf – upload and index a PDF
  - POST /ask – ask a question (optionally about a specific PDF)
  - POST /compare – compare selected products
  - GET /ner-qa – NER-based question answering for a given PDF path

  The Flask backend proxies these under /api:

  - GET /api/products
  - POST /api/index-pdf
  - POST /api/ask
  - POST /api/compare
  - GET /api/ner-qa

## Groq API Key

  doc_analysis uses Groq for LLM responses.
please make an .env file in the doc_analysis directory with the following content:

  ```
  GROQ_API_KEY=gsk_.........
  ```

## Indexing a PDF (we need sth in the db first)

  From the host:

  curl.exe -X POST "http://localhost:9000/index-pdf" `
    -F "pdf=@C:\Users\User\PycharmProjects\BeerOverflow\doc_analysis\data\deposit-agreements.pdf"