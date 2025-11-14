import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()
env_local_path = Path(__file__).resolve().parent.parent / '.env.local'
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_local_path, encoding='utf-8')
load_dotenv(dotenv_path=env_path, encoding='utf-8')


# Groq
groq_api_key: Optional[str] = str(Path(os.getenv("GROQ_API_KEY")))
groq_model: str = "llama-3.3-70b-versatile"

