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
