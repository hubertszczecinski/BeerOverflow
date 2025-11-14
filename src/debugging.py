from __future__ import annotations

from typing import List, Optional
import stable_whisper

import typer

from pipeline import (
  index_pdf,
  answer_question,
  list_all_products,
  compare_products,
  answer_question_for_file,
)
from vector_store import init_db

app = typer.Typer(help="Banking PDF Q&A service CLI")


@app.command("init-db")
def cmd_init_db():
  """Create DB tables."""
  init_db()
  typer.echo("Database initialized.")


@app.command("index-pdf")
def cmd_index_pdf(pdf_path: str = typer.Argument(..., help="Path to banking PDF.")):
  index_pdf(pdf_path)

@app.command("remove-pdf")
def cmd_remove_pdf(pdf_path: str = typer.Argument(..., help="pdf path to remove.")):
  from vector_store import delete_pdf
  delete_pdf(pdf_path=pdf_path)
  typer.echo(f"Product with ID {pdf_path} removed.")


@app.command("ask")
def cmd_ask(
    question: str = typer.Argument(..., help="User question."),
    top_k: int = typer.Option(8, help="Number of chunks to retrieve."),
    product_id: Optional[int] = typer.Option(
        None, "--product-id", "-p", help="Optional product id to focus the question on."
    ),
):
    if product_id is not None:
        answer = answer_question_for_file(product_id, question, top_k=top_k)
    else:
        answer = answer_question(question, top_k=top_k)
    typer.echo("\nANSWER:\n")
    typer.echo(answer)


@app.command("list-products")
def cmd_list_products():
  products = list_all_products()
  if not products:
      typer.echo("No products found. Index some PDFs first.")
      return
  for p in products:
      typer.echo(f"[{p['id']}] {p['type'] or '?'} - {p['name']} ({p['pdf_path']})")


@app.command("compare")
def cmd_compare(
  product_ids: List[int] = typer.Argument(..., help="Product IDs to compare."),
  question: Optional[str] = typer.Option(
      None,
      help="Optional extra question, e.g. 'Which is better for a student?'",
  ),
):
  if not question:
      question = "Compare these products in terms of price, fees, duration and who they are best for."
  answer = compare_products(product_ids, question)
  typer.echo("\nCOMPARISON:\n")
  typer.echo(answer)


def main():
    pdf_path = r"C:\Users\test-tw\PycharmProjects\BeerOverflow\data\Regulamin_Lokaty_INGBusOL_eng.pdf"
    pdf_path = r"C:\Users\test-tw\PycharmProjects\BeerOverflow\data\TermDeposit_ADB202.pdf"
    # index_pdf(pdf_path)
    question = "tell me all you know"
    top_k = 28

    if pdf_path is not None:
        answer = answer_question_for_file(pdf_path, question, top_k=top_k)
    else:
        answer = answer_question(question, top_k=top_k)
    typer.echo("\nANSWER:\n")
    typer.echo(answer)


if __name__ == "__main__":
  main()
