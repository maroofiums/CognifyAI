import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "CognifyAI"
    DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./cognify.db")

settings = Settings()