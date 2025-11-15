import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()
env_local_path = Path(__file__).resolve().parent.parent / '.env.local'
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_local_path, encoding='utf-8')
load_dotenv(dotenv_path=env_path, encoding='utf-8')



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BANKING_QA_", env_file=None, extra="ignore")

    # Paths
    data_dir: Path = Path("./data")
    db_url: str = "sqlite:///./banking_qa.db"

    # HF models
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ner_model_name: str = "boltuix/NeuroBERT-NER"

    # Groq
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    groq_model: str = "llama-3.3-70b-versatile"

    # Chunking (character-based; used as fallback)
    chunk_max_chars: int = 1200
    chunk_overlap_chars: int = 200
    # Segmentation (token-based chunking)
    segmentation_tokenizer_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    segment_max_tokens: int = 400
    segment_overlap_tokens: int = 80
    # Answer-time context windows (merge adjacent chunks)
    neighbor_window_size: int = 1

    # Retrieval
    top_k_default: int = 28


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    s.data_dir.mkdir(parents=True, exist_ok=True)
    return s
