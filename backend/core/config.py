
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application."""

    VERSION: str = "1.0"
    LOGGING_DIR: str = "logs"
    MODEL_NAME: str = "gpt-4.1-mini"
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-large"


    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    LANGSMITH_API_KEY: str
    PINECONE_INDEX_NAME: str


    class Config:
        env_file = ".env"


settings = Settings()