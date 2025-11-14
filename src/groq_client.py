from __future__ import annotations

from typing import List, Dict, Any

from groq import Groq

from config import get_settings

settings = get_settings()


class GroqClient:
  def __init__(self) -> None:
      if not settings.groq_api_key:
          raise RuntimeError("GROQ API key is not set (env: BANKING_QA_GROQ_API_KEY).")
      self.client = Groq(api_key=settings.groq_api_key)

  def chat(
      self,
      messages: List[Dict[str, str]],
      model: str | None = None,
      temperature: float = 0.1,
      max_tokens: int = 512,
  ) -> str:
      mdl = model or settings.groq_model
      resp = self.client.chat.completions.create(
          model=mdl,
          messages=messages,
          temperature=temperature,
          max_tokens=max_tokens,
      )
      return resp.choices[0].message.content

  def ask_with_context(self, question: str, context: str) -> str:
      system_prompt = (
          "You are an assistant that answers questions about banking regulations, "
          "deposit products, and credits, based ONLY on the provided context. "
          "Be concise and explicit about fees, durations, and conditions."
      )
      messages = [
          {"role": "system", "content": system_prompt},
          {
              "role": "user",
              "content": f"Context:\n{context}\n\nQuestion: {question}",
          },
      ]
      return self.chat(messages)

  def compare_products(self, products_json: str, question: str) -> str:
      system_prompt = (
          "You compare banking products (deposits, credits) using structured JSON data. "
          "Highlight differences in price, fees, durations, eligibility, and risks."
      )
      messages = [
          {"role": "system", "content": system_prompt},
          {
              "role": "user",
              "content": f"Products JSON:\n{products_json}\n\nUser question: {question}",
          },
      ]
      return self.chat(messages)