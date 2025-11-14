from __future__ import annotations

from typing import List, Dict, Any

from groq import Groq


settings = __import__('config')
groq_api_key = settings.groq_api_key


class GroqClient:
  def __init__(self) -> None:
      self.client = Groq(api_key=groq_api_key)

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


if __name__ == "__main__":
    groq_client = GroqClient()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]
    response = groq_client.chat(messages)
    print("Response from Groq model:", response)