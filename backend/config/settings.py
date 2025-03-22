import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Vector Database Settings
VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vector_stores")
CASE_LAW_DB_PATH = os.path.join(VECTOR_DB_PATH, "case_law")
STATUTES_DB_PATH = os.path.join(VECTOR_DB_PATH, "statutes")
REGULATIONS_DB_PATH = os.path.join(VECTOR_DB_PATH, "regulations")

# Model Settings
EMBED_MODEL = "embed-english-v3.0"
CHAT_MODEL = "command"
RERANK_MODEL = "rerank-english-v2.0"

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true" 